import re

def generate_script_structure(requirement_text, framework="selenium_java"):
    # 1. Parse Feature File for steps
    step_keywords = ["Given", "When", "Then", "And"]
    step_pattern = re.compile(r'^(?:' + '|'.join(step_keywords) + r')\s+(.+)', re.IGNORECASE)
    steps = set()
    for line in requirement_text.splitlines():
        match = step_pattern.match(line.strip())
        if match:
            step_text = match.group(0).strip()
            steps.add(step_text)
    if not steps:
        raise ValueError("No Gherkin steps found in Feature File.")

    # 2. Generate framework-specific code for each step
    code_lines = []
    for step in sorted(steps):
        keyword_match = re.match(r'^(Given|When|Then|And)\s+(.+)', step, re.IGNORECASE)
        if not keyword_match:
            continue
        keyword = keyword_match.group(1)
        step_text = keyword_match.group(2)
        step_name = re.sub(r'[^a-zA-Z0-9_]', '_', step_text.lower())[:40]

        # Simple heuristics for code generation
        if "homepage" in step_text or "home page" in step_text:
            nav_code = {
                "selenium_java": f'    driver.get("<URL>"); // TODO: Set homepage URL\n    assert driver.getTitle() != null; // TODO: Check title',
                "selenium_python": f'    driver.get("<URL>")  # TODO: Set homepage URL\n    assert driver.title is not None  # TODO: Check title',
                "playwright_python": f'    page.goto("<URL>")  # TODO: Set homepage URL\n    assert page.title() is not None  # TODO: Check title'
            }
            action_code = nav_code.get(framework, "    # TODO: Implement navigation")
        elif "enter" in step_text or "type" in step_text:
            action_code = {
                "selenium_java": f'    WebElement el = driver.findElement(By.id("<element_id>")); // TODO: Set correct locator\n    el.sendKeys("<value>");',
                "selenium_python": f'    el = driver.find_element(By.ID, "<element_id>")  # TODO: Set correct locator\n    el.send_keys("<value>")',
                "playwright_python": f'    page.fill("#<element_id>", "<value>")  # TODO: Set correct locator'
            }.get(framework, "    # TODO: Implement input")
        elif "click" in step_text:
            action_code = {
                "selenium_java": f'    driver.findElement(By.id("<element_id>")).click(); // TODO: Set correct locator',
                "selenium_python": f'    driver.find_element(By.ID, "<element_id>").click()  # TODO: Set correct locator',
                "playwright_python": f'    page.click("#<element_id>")  # TODO: Set correct locator'
            }.get(framework, "    # TODO: Implement click")
        elif "see" in step_text or "should" in step_text or "verify" in step_text or "assert" in step_text:
            action_code = {
                "selenium_java": f'    WebElement el = driver.findElement(By.id("<element_id>")); // TODO: Set correct locator\n    assert el.isDisplayed();',
                "selenium_python": f'    el = driver.find_element(By.ID, "<element_id>")  # TODO: Set correct locator\n    assert el.is_displayed()',
                "playwright_python": f'    el = page.locator("#<element_id>")  # TODO: Set correct locator\n    assert el.is_visible()'
            }.get(framework, "    # TODO: Implement assertion")
        else:
            action_code = "    # TODO: Implement step logic"

        if framework == "selenium_java":
            code_lines.append(f'@{keyword}("{step_text}")\npublic void {step_name}() {{\n{action_code}\n    // {step_text}\n}}\n')
        elif framework == "selenium_python":
            code_lines.append(f'@{keyword.lower()}("{step_text}")\ndef step_impl(context):\n{action_code}\n    # {step_text}\n')
        elif framework == "playwright_python":
            code_lines.append(f'@{keyword.lower()}("{step_text}")\ndef step_impl(context):\n    from playwright.sync_api import sync_playwright\n    with sync_playwright() as p:\n        # Playwright context setup\n        browser = p.chromium.launch()\n        page = browser.new_page()\n{action_code}\n        # {step_text}\n        browser.close()\n')
        else:
            code_lines.append(f'# Unknown framework: {framework}\n# Step: {step}\n')

    generated_code = '\n'.join(code_lines)
    ext = "java" if framework == "selenium_java" else "py"
    file_name = f"steps/step_definitions_{framework}.{ext}"
    return {
        "folder_structure": ["steps"],
        "files_to_create": {
            file_name: generated_code
        }
    }
