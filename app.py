
import streamlit as st
import math
import ast
import operator

# =====================================
# 1. PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Scientific Calculator",
    page_icon="🧮",
    layout="centered"
)

# =====================================
# 2. LOAD CSS
# =====================================

with open("style.css", "r", encoding="utf-8") as file:
    st.markdown(
        f"<style>{file.read()}</style>",
        unsafe_allow_html=True
    )

# =====================================
# 3. SAFE CALCULATION ENGINE
# =====================================

def calculate(expression, degree_mode=True):

    if len(expression) > 300:
        raise ValueError("Expression terlalu panjang")

    tree = ast.parse(expression, mode="eval")

    def safe_eval(node):

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Angka tidak valid")
            return node.value

        if isinstance(node, ast.Name):

            constants = {
                "pi": math.pi,
                "e": math.e
            }

            if node.id in constants:
                return constants[node.id]

            raise ValueError("Konstanta tidak dikenal")

        if isinstance(node, ast.BinOp):

            left = safe_eval(node.left)
            right = safe_eval(node.right)

            operations = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod
            }

            operation = operations.get(type(node.op))

            if operation is None:
                raise ValueError("Operasi tidak didukung")

            if isinstance(node.op, ast.Pow):
                if abs(right) > 100 or abs(left) > 1e100:
                    raise ValueError("Pangkat terlalu besar")

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            value = safe_eval(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

            raise ValueError("Operator tidak didukung")

        if isinstance(node, ast.Call):

            if not isinstance(node.func, ast.Name):
                raise ValueError("Fungsi tidak valid")

            if node.keywords:
                raise ValueError("Argumen tidak didukung")

            name = node.func.id
            args = [safe_eval(arg) for arg in node.args]

            def sin(x):
                return math.sin(
                    math.radians(x) if degree_mode else x
                )

            def cos(x):
                return math.cos(
                    math.radians(x) if degree_mode else x
                )

            def tan(x):
                return math.tan(
                    math.radians(x) if degree_mode else x
                )

            functions = {
                "sin": sin,
                "cos": cos,
                "tan": tan,
                "sqrt": math.sqrt,
                "log": math.log10,
                "ln": math.log,
                "abs": abs,
                "factorial": math.factorial
            }

            if name == "log" and len(args) == 2:
                return math.log(args[0], args[1])

            if name not in functions:
                raise ValueError("Fungsi tidak dikenal")

            if name == "factorial":

                if (
                    len(args) != 1
                    or args[0] < 0
                    or not float(args[0]).is_integer()
                    or args[0] > 170
                ):
                    raise ValueError("Input faktorial tidak valid")

                args[0] = int(args[0])

            if name != "log" and len(args) != 1:
                raise ValueError("Jumlah argumen tidak sesuai")

            return functions[name](*args)

        raise ValueError("Ekspresi tidak valid")

    result = safe_eval(tree.body)

    if isinstance(result, complex):
        raise ValueError("Hasil kompleks tidak didukung")

    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("Hasil tidak terdefinisi")

    return result


# =====================================
# 4. SESSION STATE
# =====================================

if "expression" not in st.session_state:
    st.session_state.expression = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


def add_value(value):
    st.session_state.expression += value


def clear_expression():
    st.session_state.expression = ""


def delete_last():
    st.session_state.expression = (
        st.session_state.expression[:-1]
    )


# =====================================
# 5. CALCULATOR HEADER
# =====================================

st.title("SCIENTIFIC CALCULATOR")

st.markdown(
    '<p class="subtitle">Advanced Mathematical Calculator</p>',
    unsafe_allow_html=True
)

mode = st.radio(
    "Angle Mode",
    ["DEG", "RAD"],
    horizontal=True
)

degree_mode = mode == "DEG"


# =====================================
# 6. CALCULATOR DISPLAY
# =====================================

st.text_input(
    "Expression",
    key="expression",
    placeholder="Enter your calculation..."
)


# =====================================
# 7. CALCULATOR BUTTONS
# =====================================

buttons = [
    ["AC", "DEL", "(", ")", "÷"],
    ["sin(", "cos(", "tan(", "sqrt(", "×"],
    ["log(", "ln(", "pi", "e", "−"],
    ["7", "8", "9", "^", "+"],
    ["4", "5", "6", "factorial(", "Mod"],
    ["1", "2", "3", "0", "."],
    ["00", "Ans", "=", "", ""]
]

previous_result = (
    st.session_state.history[0][1]
    if st.session_state.history else None
)

for row in buttons:

    cols = st.columns(5)

    for i, button in enumerate(row):

        if not button:
            continue

        with cols[i]:

            if button == "AC":

                st.button(
                    button,
                    key="clear",
                    on_click=clear_expression
                )

            elif button == "DEL":

                st.button(
                    button,
                    key="delete",
                    on_click=delete_last
                )

            elif button == "=":

                if st.button(button, key="equals"):

                    try:

                        expression = (
                            st.session_state.expression
                            .replace("×", "*")
                            .replace("÷", "/")
                            .replace("−", "-")
                            .replace("^", "**")
                            .replace("Mod", "%")
                        )

                        result = calculate(
                            expression,
                            degree_mode
                        )

                        st.session_state.history.insert(
                            0, (expression, result)
                        )

                        st.session_state.last_result = result

                    except Exception as error:

                        st.error(
                            f"Calculation error: {error}"
                        )

            elif button == "Ans":

                if previous_result is not None:

                    st.button(
                        button,
                        key="answer",
                        on_click=add_value,
                        args=(f"({previous_result})",)
                    )

                else:

                    st.button(
                        button,
                        disabled=True,
                        key="answer"
                    )

            else:

                st.button(
                    button,
                    key=f"btn_{button}",
                    on_click=add_value,
                    args=(button,)
                )


# =====================================
# 8. RESULT DISPLAY
# =====================================

if st.session_state.last_result is not None:

    st.markdown(
        f"""
        <div class="result-box">
            <div class="result-label">RESULT</div>
            <div class="result-value">
                {st.session_state.last_result}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================
# 9. CALCULATION HISTORY
# =====================================

st.markdown("---")

st.subheader("Calculation History")

if st.session_state.history:

    for expression, result in st.session_state.history[:5]:

        st.write(f"**{expression} = {result}**")

else:

    st.caption(
        "Your calculation history will appear here."
    )
