import streamlit as st
import ast
import os
import time
import random
from dotenv import load_dotenv
from groq import Groq

# --------------------------------------------------
# 1. LOAD GROQ API
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key:
    client = Groq(api_key=api_key)
else:
    client = None


# --------------------------------------------------
# 2. PAGE SETTINGS
# --------------------------------------------------
# Detect Errors
def detect_errors(code):
    try:
        ast.parse(code)
    except SyntaxError as error:
        return (
            f"Syntax Error on line {error.lineno}: "
            f"{error.msg}"
        )

    prompt = (
        "Check this Python code for possible bugs and logical errors. "
        "Explain any problems simply. Do not claim that you executed it.\n\n"
        + code
    )

    return get_ai_explanation(prompt)


# Improve Code
def improve_code(code):
    prompt = (
        "Suggest improvements for this Python code. "
        "Explain the improvements and provide an improved version.\n\n"
        + code
    )

    return get_ai_explanation(prompt)

st.set_page_config(
    page_title="AI Code Explainer",
    page_icon="💻",
    layout="wide"
)

st.title("💻 AI Code Explainer")
st.subheader("Understand, Debug and Improve Your Python Code")

st.write(
    "Upload a Python file or paste your code below "
    "to understand, debug and improve your code."
)


# --------------------------------------------------
# 3. GROQ AI FUNCTION
# --------------------------------------------------

def ask_groq(prompt, system_message, max_tokens=2000):
    """Send a prompt to Groq and return its response."""

    if client is None:
        return "Groq API key not found. Please check your .env file."

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=max_tokens,
                timeout=60
            )

            answer = response.choices[0].message.content

            if answer:
                return answer

            return "The AI returned an empty response."

        except Exception as error:
            message = str(error).lower()

            temporary_error = any(
                word in message
                for word in [
                    "429", "500", "502", "503", "504",
                    "timeout", "connection", "rate limit",
                    "temporarily unavailable"
                ]
            )

            if temporary_error and attempt < max_attempts - 1:
                time.sleep((2 ** attempt) + random.uniform(0, 1))
            else:
                return f"Groq API error: {error}"

    return "The AI could not respond after 3 attempts."


# --------------------------------------------------
# 4. AI EXPLANATION
# --------------------------------------------------

def get_ai_explanation(code):
    return ask_groq(
        prompt=f"Explain this Python code:\n\n{code}",
        system_message=(
            "You are a Python programming teacher. "
            "Explain the code in simple English. "
            "Describe its purpose, important lines, variables, "
            "functions, parameters and expected output. "
            "Do not execute the code. Do not invent output "
            "when it cannot be determined."
        ),
        max_tokens=2000
    )


# --------------------------------------------------
# 5. CODE ERROR DETECTOR
# --------------------------------------------------

def detect_code_errors(code):
    """Check syntax locally and ask AI about likely issues."""

    try:
        ast.parse(code)

    except SyntaxError as error:
        return (
            "## Syntax Error Found\n\n"
            f"- **Error:** {error.msg}\n"
            f"- **Line:** {error.lineno}\n"
            f"- **Column:** {error.offset}\n\n"
            "Correct the syntax error and check the code again."
        )

    return ask_groq(
        prompt=(
            "Review this Python code for likely runtime errors, "
            "undefined variables, logical mistakes and common bugs.\n\n"
            f"Python code:\n{code}"
        ),
        system_message=(
            "You are a careful Python debugging assistant. "
            "Identify specific potential errors and explain why "
            "they may occur. Suggest fixes where possible. "
            "If you do not find a clear issue, say so. "
            "Do not execute the code. Distinguish confirmed syntax "
            "errors from potential runtime or logical problems. "
            "Static review cannot guarantee that code is error-free."
        ),
        max_tokens=2000
    )


# --------------------------------------------------
# 6. CODE IMPROVEMENT SUGGESTIONS
# --------------------------------------------------

def suggest_code_improvements(code):
    return ask_groq(
        prompt=(
            "Review this Python code and suggest practical "
            "improvements for readability, maintainability, "
            "performance and Python best practices.\n\n"
            f"Python code:\n{code}"
        ),
        system_message=(
            "You are an experienced Python code reviewer. "
            "Give beginner-friendly suggestions in simple English. "
            "Explain why each suggestion is useful. "
            "Include a small corrected example when appropriate. "
            "Do not execute the code. Do not claim performance "
            "improvements without a reasonable explanation."
        ),
        max_tokens=2000
    )


# --------------------------------------------------
# 7. FILE UPLOADER AND CODE INPUT
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "📂 Upload Python File",
    type=["py"]
)

default_code = '''def square(number):
    return number * number

print(square(5))
'''

if uploaded_file is not None:
    try:
        uploaded_code = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        uploaded_code = ""
        st.error(
            "Unable to read this file. "
            "Please upload a UTF-8 Python file."
        )
else:
    uploaded_code = default_code

code = st.text_area(
    "📝 Paste Your Python Code Here",
    value=uploaded_code,
    height=250,
    key="python_code"
)


# --------------------------------------------------
# 8. ANALYSIS BUTTONS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    explain_button = st.button(
        "🔍 Explain Code",
        type="primary",
        use_container_width=True
    )

with col2:
    error_button = st.button(
        "🐞 Detect Errors",
        use_container_width=True
    )

with col3:
    improve_button = st.button(
        "🚀 Improve Code",
        use_container_width=True
    )


# --------------------------------------------------
# 9. RUN ANALYSIS
# --------------------------------------------------

if explain_button or error_button or improve_button:

    if not code.strip():
        st.warning("Please enter or upload some Python code.")

    else:
        # Keep the latest results for the report.
        st.session_state["report_code"] = code

        # Explain Code
        if explain_button:
            try:
                tree = ast.parse(code)
                lines = code.splitlines()

                functions = [
                    node for node in ast.walk(tree)
                    if isinstance(
                        node,
                        (ast.FunctionDef, ast.AsyncFunctionDef)
                    )
                ]

                classes = [
                    node for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ]

                print_count = sum(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "print"
                    for node in ast.walk(tree)
                )

                imports = [
                    node for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                ]

                # CODE SUMMARY
                st.markdown("## 1. 📊 Code Summary")

                a, b, c, d, e = st.columns(5)

                a.metric("Total Lines", len(lines))
                b.metric("Functions", len(functions))
                c.metric("Classes", len(classes))
                d.metric("Print Calls", print_count)
                e.metric("Imports", len(imports))

                summary = (
                    f"Total lines: {len(lines)}\n"
                    f"Total functions: {len(functions)}\n"
                    f"Total classes: {len(classes)}\n"
                    f"Print calls: {print_count}\n"
                    f"Import statements: {len(imports)}"
                )

                st.session_state["report_summary"] = summary

                # AI EXPLANATION
                st.markdown("## 2. 🤖 AI-Powered Explanation")

                with st.spinner("AI is explaining your code..."):
                    explanation = get_ai_explanation(code)

                st.markdown(explanation)
                st.session_state["report_explanation"] = explanation

                # LINE-BY-LINE EXPLANATION
                st.markdown("## 3. 📝 Line-by-Line Explanation")

                line_report = []

                for line_number, line in enumerate(lines, start=1):
                    stripped = line.strip()

                    if not stripped:
                        continue

                    st.markdown(f"**Line {line_number}:**")
                    st.code(line, language="python")

                    if stripped.startswith("async def "):
                        function_name = (
                            stripped[len("async def "):]
                            .split("(")[0].strip()
                        )
                        line_explanation = (
                            f"This line defines the asynchronous "
                            f"function '{function_name}'."
                        )

                    elif stripped.startswith("def "):
                        function_name = (
                            stripped[4:].split("(")[0].strip()
                        )
                        line_explanation = (
                            f"This line defines the function "
                            f"'{function_name}'."
                        )

                    elif stripped.startswith("class "):
                        class_name = (
                            stripped[6:].split("(")[0]
                            .split(":")[0].strip()
                        )
                        line_explanation = (
                            f"This line defines the class '{class_name}'."
                        )

                    elif stripped.startswith("return"):
                        line_explanation = (
                            "This line returns a value from a function."
                        )

                    elif stripped.startswith("print("):
                        line_explanation = (
                            "This line displays output on the screen."
                        )

                    elif stripped.startswith("import "):
                        line_explanation = (
                            "This line imports a Python module."
                        )

                    elif stripped.startswith("from "):
                        line_explanation = (
                            "This line imports specific items from a module."
                        )

                    elif stripped.startswith("#"):
                        line_explanation = (
                            "This is a comment. Python does not execute it."
                        )

                    elif "=" in stripped and "==" not in stripped:
                        variable = stripped.split("=", 1)[0].strip()
                        line_explanation = (
                            f"This line assigns a value to '{variable}'."
                        )

                    else:
                        line_explanation = (
                            "This line is part of the program logic."
                        )

                    st.write(line_explanation)

                    line_report.append(
                        f"Line {line_number}: {line}\n"
                        f"Explanation: {line_explanation}"
                    )

                st.session_state["report_line_explanation"] = (
                    "\n\n".join(line_report)
                )

                # FUNCTION ANALYSIS
                st.markdown("## 4. 🧩 Function Analysis")

                function_report = []

                if functions:
                    for function in functions:
                        st.markdown(f"### Function: `{function.name}`")

                        parameters = [
                            arg.arg for arg in function.args.args
                        ]

                        if parameters:
                            parameter_text = ", ".join(parameters)
                        else:
                            parameter_text = "None"

                        st.write(f"**Parameters:** {parameter_text}")
                        st.write(f"**Defined on line:** {function.lineno}")

                        function_report.append(
                            f"Function: {function.name}\n"
                            f"Parameters: {parameter_text}\n"
                            f"Defined on line: {function.lineno}"
                        )

                else:
                    st.info("No function definitions found.")
                    function_report.append("No function definitions found.")

                st.session_state["report_functions"] = (
                    "\n\n".join(function_report)
                )

                # DOCUMENTATION
                st.markdown("## 5. 📚 Documentation")
                st.code(code, language="python")

                st.session_state["report_documentation"] = (
                    "## Source Code\n\n"
                    "```python\n"
                    f"{code}\n"
                    "```"
                )

                st.success("Code explanation completed successfully!")

            except SyntaxError as error:
                message = (
                    f"Python syntax error on line {error.lineno}: "
                    f"{error.msg}"
                )

                st.error(message)
                st.session_state["report_errors"] = message

        # ERROR DETECTOR
        if error_button:
            st.markdown("## 6. 🐞 Code Error Detector")

            try:
                ast.parse(code)
                st.success(
                    "No Python syntax errors detected by the parser."
                )
            except SyntaxError:
                pass

            with st.spinner("Checking your code for possible errors..."):
                error_result = detect_code_errors(code)

            st.markdown(error_result)
            st.session_state["report_errors"] = error_result

        # IMPROVEMENT SUGGESTIONS
        if improve_button:
            st.markdown("## 7. 🚀 Code Improvement Suggestions")

            with st.spinner("Finding ways to improve your code..."):
                improvement_result = suggest_code_improvements(code)

            st.markdown(improvement_result)
            st.session_state["report_improvements"] = improvement_result


# --------------------------------------------------
# 10. DOWNLOAD FULL REPORT
# --------------------------------------------------

st.markdown("---")
st.markdown("## 8. 📥 Download Report")

st.write(
    "Download the analysis results that have been generated "
    "during this session."
)

report_parts = [
    "# AI Code Explainer Report",
    "",
    "## Source Code",
    "```python",
    st.session_state.get("report_code", code),
    "```",
]

if st.session_state.get("report_summary"):
    report_parts.extend([
        "",
        "## Code Summary",
        st.session_state["report_summary"]
    ])

if st.session_state.get("report_explanation"):
    report_parts.extend([
        "",
        "## AI Explanation",
        st.session_state["report_explanation"]
    ])

if st.session_state.get("report_line_explanation"):
    report_parts.extend([
        "",
        "## Line-by-Line Explanation",
        st.session_state["report_line_explanation"]
    ])

if st.session_state.get("report_functions"):
    report_parts.extend([
        "",
        "## Function Analysis",
        st.session_state["report_functions"]
    ])

if st.session_state.get("report_errors"):
    report_parts.extend([
        "",
        "## Code Error Detector",
        st.session_state["report_errors"]
    ])

if st.session_state.get("report_improvements"):
    report_parts.extend([
        "",
        "## Code Improvement Suggestions",
        st.session_state["report_improvements"]
    ])

report_text = "\n".join(report_parts)

st.download_button(
    label="📥 Download Full Report",
    data=report_text,
    file_name="AI_Code_Explainer_Report.md",
    mime="text/markdown",
    use_container_width=True
)

st.caption(
    "Note: AI suggestions are advisory. Review them before changing "
    "or running your code. The error detector does not execute code."
)
