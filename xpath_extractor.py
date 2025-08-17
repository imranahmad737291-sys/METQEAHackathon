import os
import base64
import logging
import tempfile
import io
from PIL import Image

def is_important_element(el):
    """
    Returns True if the element qualifies as important.
    Criteria:
    - Interactive tags: button, a, input, select, textarea
    - Stable attributes: id, name, data-*, aria-*, role
    - Meaningful visible text (length > 0, not just whitespace)
    - Text matches business keywords
    """
    tag = el.tag_name.lower()
    interactive_tags = {"button", "a", "input", "select", "textarea"}
    if tag in interactive_tags:
        return True
    # Stable attributes
    attrs = el.get_attribute('outerHTML')
    import re
    if re.search(r'\s(id|name|role|data-[\w-]+|aria-[\w-]+)="[^"]+"', attrs):
        return True
    # Meaningful text
    text = el.text.strip()
    if len(text) > 0:
        # Business keywords
        keywords = ["login", "signin", "search", "cart", "checkout", "buy", "submit"]
        for kw in keywords:
            if kw in text.lower():
                return True
        # Otherwise, just meaningful text
        return True
    return False
def extract_xpaths(url, important_only=False):
    """
    Extracts interactive elements and metadata from the given URL using Selenium headless Chrome.
    Returns a list of dicts with tag, xpath, text, attributes, thumbnail_b64, screenshot_path, element_index.
    If important_only=True, filters elements using is_important_element().
    """
    driver = None
    results = []
    try:
        driver = start_browser(url)
        selectors = [
            'a', 'button', 'input', 'textarea', 'select', '[onclick]'
        ]
        elements = []
        from selenium.webdriver.common.by import By
        for selector in selectors:
            found = driver.find_elements(By.CSS_SELECTOR, selector)
            elements.extend(found)
        # Remove duplicates
        unique_elements = list({el: None for el in elements}.keys())
        if important_only:
            unique_elements = [el for el in unique_elements if is_important_element(el)]
        temp_dir = tempfile.mkdtemp(prefix="xpath_screenshots_")
        for idx, el in enumerate(unique_elements):
            try:
                tag = el.tag_name
                text = el.text.strip()
                outer_html = el.get_attribute('outerHTML')
                # Robust relative XPath
                xpath = get_robust_xpath(driver, el)
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                import time
                time.sleep(0.2)
                # Screenshot
                loc = el.location_once_scrolled_into_view
                size = el.size
                png = driver.get_screenshot_as_png()
                im = Image.open(io.BytesIO(png))
                left = int(loc['x'])
                top = int(loc['y'])
                right = left + int(size['width'])
                bottom = top + int(size['height'])
                element_img = im.crop((left, top, right, bottom))
                thumb = element_img.copy()
                thumb.thumbnail((80, 80))
                thumb_path = os.path.join(temp_dir, f"thumb_{idx}.png")
                element_path = os.path.join(temp_dir, f"element_{idx}.png")
                thumb.save(thumb_path, format="PNG", optimize=True)
                element_img.save(element_path, format="PNG", optimize=True)
                with open(thumb_path, "rb") as f:
                    thumb_b64 = base64.b64encode(f.read()).decode()
                results.append({
                    'tag': tag,
                    'xpath': xpath,
                    'text': text,
                    'attributes': outer_html,
                    'thumbnail_b64': thumb_b64,
                    'screenshot_path': element_path,
                    'element_index': idx
                })
            except Exception as ex:
                logging.exception(f"Error extracting element {idx}")
                continue
    except Exception as e:
        logging.exception(f"Error extracting xpaths from {url}")
    finally:
        # Do not quit driver, keep persistent for session
        pass
    return results

def get_robust_xpath(driver, element):
    """
    Generate a robust relative XPath for the element, preferring id, name, aria-label, data-testid, etc.
    """
    from selenium.webdriver.common.by import By
    tag = element.tag_name
    # 1. Prefer id if stable
    id_val = element.get_attribute('id')
    if id_val and not id_val.isdigit() and not any(c.isdigit() for c in id_val):
        xpath = f"//{tag}[@id='{id_val}']"
        found = driver.find_elements(By.XPATH, xpath)
        if len(found) == 1 and found[0] == element:
            return xpath

        def is_important_element(el):
            """
            Returns True if the element qualifies as important.
            Criteria:
            - Interactive tags: button, a, input, select, textarea
            - Stable attributes: id, name, data-*, aria-*, role
            - Meaningful visible text (length > 0, not just whitespace)
            - Text matches business keywords
            """
            tag = el.tag_name.lower()
            interactive_tags = {"button", "a", "input", "select", "textarea"}
            if tag in interactive_tags:
                return True
            # Stable attributes
            attrs = el.get_attribute('outerHTML')
            import re
            import base64
            import io
            import tempfile
            import logging
            from PIL import Image

            def is_important_element(el):
                """
                Returns True if the element qualifies as important.
                Criteria:
                - Interactive tags: button, a, input, select, textarea
                - Stable attributes: id, name, data-*, aria-*, role
                - Meaningful visible text (length > 0, not just whitespace)
                - Text matches business keywords
                """
                tag = el.tag_name.lower()
                interactive_tags = {"button", "a", "input", "select", "textarea"}
                if tag in interactive_tags:
                    return True
                # Stable attributes
                attrs = el.get_attribute('outerHTML')
                import re
                if re.search(r'\s(id|name|role|data-[\w-]+|aria-[\w-]+)="[^"]+"', attrs):
                    return True
                # Meaningful text
                text = el.text.strip()
                if len(text) > 0:
                    # Business keywords
                    keywords = ["login", "signin", "search", "cart", "checkout", "buy", "submit"]
                    for kw in keywords:
                        if kw in text.lower():
                            return True
                    # Otherwise, just meaningful text
                    return True
                return False
                # Business keywords
                keywords = ["login", "signin", "search", "cart", "checkout", "buy", "submit"]
                for kw in keywords:
                    if kw in text.lower():
                        return True
                # Otherwise, just meaningful text
                return True
            return False
    # 2. Prefer name
    name_val = element.get_attribute('name')
    if name_val:
        xpath = f"//{tag}[@name='{name_val}']"
        found = driver.find_elements(By.XPATH, xpath)
        if len(found) == 1 and found[0] == element:
            return xpath
    # 3. Prefer data-* and aria-* attributes
    attribs = element.get_attribute('outerHTML')
    import re
    data_attrs = re.findall(r'data-([\w-]+)="([^"]+)"', attribs)
    aria_attrs = re.findall(r'aria-([\w-]+)="([^"]+)"', attribs)
    attr_parts = []
    for k, v in data_attrs:
        attr_parts.append(f"@data-{k}='{v}'")
    for k, v in aria_attrs:
        attr_parts.append(f"@aria-{k}='{v}'")
    # 4. Prefer stable class names (avoid auto-generated)
    class_val = element.get_attribute('class')
    if class_val:
        classes = [c for c in class_val.split() if len(c) > 2 and not re.search(r'\d', c)]
        if classes:
            class_expr = " and ".join([f"contains(concat(' ', normalize-space(@class), ' '), ' {cls} ')" for cls in classes])
            attr_parts.append(class_expr)
    # Combine multiple attributes if needed
    if attr_parts:
        xpath = f"//{tag}[{' and '.join(attr_parts)}]"
        found = driver.find_elements(By.XPATH, xpath)
        if len(found) == 1 and found[0] == element:
            return xpath
    # 5. Fallback to text
    text = element.text.strip()
    if text:
        safe_text = text.replace("'", "\'")
        xpath = f"//{tag}[contains(normalize-space(text()), '{safe_text}') ]"
        found = driver.find_elements(By.XPATH, xpath)
        if len(found) == 1 and found[0] == element:
            return xpath
    # 6. Fallback to parent-child relationship
    try:
        parent = element.find_element(By.XPATH, '..')
        siblings = parent.find_elements(By.XPATH, f'./{tag}')
        if len(siblings) > 1:
            idx = siblings.index(element) + 1
            xpath = f"//{tag}[{idx}]"
            found = driver.find_elements(By.XPATH, xpath)
            if len(found) == 1 and found[0] == element:
                return xpath
    except Exception:
        pass
    # 7. Fallback: absolute XPath (avoid if possible)
    return driver.execute_script(
        "function absoluteXPath(element) {"
        "var comp, comps = [];"
        "var parent = null;"
        "var xpath = '';"
        "var getPos = function(element) {"
        "var position = 1, curNode;"
        "if (element.nodeType == Node.ATTRIBUTE_NODE) {"
        "return null;"
        """
        Extracts interactive elements and metadata from the given URL using Selenium headless Chrome.
        Returns a list of dicts with tag, xpath, text, attributes, thumbnail_b64, screenshot_path, element_index.
        If important_only=True, filters elements using is_important_element().
        """
        "}"
        "return position;"
        "};"
        "if (element instanceof Document) {"
        "return '/';"
        "}"
        "for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {"
        "comp = comps[comps.length] = {};"
        "switch (element.nodeType) {"
        "case Node.TEXT_NODE:"
        "comp.name = 'text()';"
        "break;"
        "case Node.ATTRIBUTE_NODE:"
        "comp.name = '@' + element.nodeName;"
        "break;"
        "case Node.PROCESSING_INSTRUCTION_NODE:"
        "comp.name = 'processing-instruction()';"
        "break;"
        "case Node.COMMENT_NODE:"
        "comp.name = 'comment()';"
        "break;"
        "case Node.ELEMENT_NODE:"
        "comp.name = element.nodeName;"
        "break;"
        "}"
        "comp.position = getPos(element);"
        "}"
        "for (var i = comps.length - 1; i >= 0; i--) {"
        "comp = comps[i];"
        "xpath += '/' + comp.name.toLowerCase();"
        "if (comp.position !== null && comp.position > 1) {"
        "xpath += '[' + comp.position + ']';"
        "}"
        "}"
        "return xpath;"
        "}"
        "return absoluteXPath(arguments[0]);",
        element)
# Persistent global driver
_global_driver = None

def start_browser(url=None, timeout=20):
    global _global_driver
    if _global_driver is not None:
        if url:
            _global_driver.get(url)
        return _global_driver
    from selenium import webdriver
    options = webdriver.ChromeOptions()
    # Remove headless mode
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    # You may add other options if needed
    _global_driver = webdriver.Chrome(options=options)
    if url:
        _global_driver.get(url)
        import time
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.common.exceptions import TimeoutException
        try:
            WebDriverWait(_global_driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)
        except TimeoutException:
            pass
    return _global_driver

def stop_browser():
    global _global_driver
    if _global_driver is not None:
        try:
            _global_driver.quit()
        except Exception:
            pass
        _global_driver = None
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# ====== SETUP SELENIUM DRIVER ======
def init_driver():
    if "driver" not in st.session_state:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        st.session_state.driver = webdriver.Chrome(options=chrome_options)
    return st.session_state.driver

# ====== EXTRACT XPATHS ======
xpath_url = st.text_input("Enter URL to extract XPaths")
extract_btn = st.button("Extract XPaths")

if extract_btn and xpath_url:
    try:
        driver = init_driver()
        driver.get(xpath_url)
        time.sleep(2)  # Wait for DOM to load
        elements = driver.find_elements("xpath", "//*")
    except Exception as e:
        st.error(f"Error loading page: {e}")

    results = []
    for el in elements:
        try:
            tag = el.tag_name
            text = el.text.strip()
            attrs = driver.execute_script(
                "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) "
                "{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;",
                el
            )
            if "id" in attrs:
                xpath = f"//*[@id='{attrs['id']}']"
            elif "name" in attrs:
                xpath = f"//*[@name='{attrs['name']}']"
            elif "class" in attrs:
                xpath = f"//*[@class='{attrs['class']}']"
            else:
                xpath = f"//{tag}"

            results.append({"tag": tag, "text": text, "xpath": xpath})
        except Exception:
            pass

    # ====== DISPLAY IN STREAMLIT ======
    for item in results:
        st.markdown(f"**Tag:** {item['tag']} | **Text:** {item['text']}")
        # Show XPath in a text_area with built-in copy-to-clipboard icon
        st.text_area(
            label="XPath",
            value=item['xpath'],
            height=30,
            label_visibility="visible",
            help="Click the copy icon to copy this XPath."
        )

        # Highlight button (keeps same driver)
        if st.button(f"Highlight: {item['xpath']}"):
            try:
                el_to_highlight = driver.find_element("xpath", item['xpath'])
                driver.execute_script("arguments[0].style.border='3px solid yellow'", el_to_highlight)
                time.sleep(2)
                driver.execute_script("arguments[0].style.border=''", el_to_highlight)
            except Exception as e:
                st.error(f"Could not highlight: {e}")

    # Download all XPaths as TXT
    if results:
        all_xpaths = '\n'.join([item['xpath'] for item in results])
        st.download_button(
            label="Download All XPaths",
            data=all_xpaths,
            file_name="all_xpaths.txt",
            mime="text/plain"
        )
