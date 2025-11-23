import json
import streamlit as st

st.set_page_config(page_title="Формирование строки IN", page_icon="➡️", layout="wide")


def normalize_items(source_text: str, remove_spaces: bool, skip_header: bool) -> list[str]:
    raw_lines = source_text.splitlines()
    cleaned: list[str] = []
    seen = set()
    for line in raw_lines:
        item = "".join(line.split()) if remove_spaces else line.strip()
        if item:
            if item not in seen:  # исключаем дубликаты, сохраняя порядок
                cleaned.append(item)
                seen.add(item)
    if skip_header and cleaned:
        cleaned = cleaned[1:]
    return cleaned


def build_output(
    source_text: str,
    delimiter: str,
    quote: str,
    keep_line_breaks: bool,
    remove_spaces: bool,
    skip_header: bool,
    wrap_in_in: bool,
) -> str:
    items = normalize_items(source_text, remove_spaces, skip_header)
    if not items:
        return ""

    items = sorted(items)
    quoted = [f"{quote}{item}{quote}" if quote else item for item in items]
    joiner = "\n" if keep_line_breaks else delimiter
    body = joiner.join(quoted)

    if wrap_in_in:
        return f"IN\n({body})"
    return body


def render_copy_script(text: str):
    """Маленькая кнопка с иконкой копирования, выполняющая копирование по клику."""
    escaped = json.dumps(text)
    st.components.v1.html(
        f"""
        <div style="width:100%; display:flex; justify-content:flex-end; align-items:flex-start; margin:0; padding:0;">
          <button id="copy-btn" style="
              display:flex;
              flex-direction:column;
              align-items:center;
              gap:6px;
              width:110px;
              padding:10px 10px;
              background:#ffffff;
              border:1px solid #cbd5e0;
              border-radius:8px;
              cursor:pointer;
              box-shadow:0 1px 2px rgba(0,0,0,0.08);
          ">
            <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#2563eb' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
              <rect x='9' y='9' width='13' height='13' rx='2' ry='2'></rect>
              <path d='M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1'></path>
            </svg>
            <span style="font-size:13px; color:#1f2937; font-weight:600;">Копировать</span>
          </button>
        </div>
        <script>
        const btn = document.getElementById('copy-btn');
        const text = {escaped};
        if (btn) {{
          btn.onclick = async () => {{
            try {{
              await navigator.clipboard.writeText(text);
              const msg = document.createElement('div');
              msg.textContent = 'Скопировано';
              msg.style.position = 'absolute';
              msg.style.top = '100%';
              msg.style.right = '0';
              msg.style.marginTop = '6px';
              msg.style.padding = '6px 10px';
              msg.style.background = '#e6ffed';
              msg.style.color = '#155724';
              msg.style.border = '1px solid #c3e6cb';
              msg.style.borderRadius = '6px';
              msg.style.boxShadow = '0 1px 2px rgba(0,0,0,0.06)';
              btn.parentElement.appendChild(msg);
              setTimeout(() => msg.remove(), 1500);
            }} catch (err) {{
              alert('Не удалось скопировать: ' + err);
              console.error(err);
            }}
          }};
        }}
        </script>
        """,
        height=100,
    )


def init_state():
    st.session_state.setdefault("source_text", "")
    st.session_state.setdefault("result_area", "")
    st.session_state.setdefault("delimiter", ",")
    st.session_state.setdefault("quote", "")
    st.session_state.setdefault("keep_line_breaks", False)
    st.session_state.setdefault("remove_spaces", False)
    st.session_state.setdefault("skip_header", False)
    st.session_state.setdefault("wrap_in_in", True)


def clear_all():
    st.session_state.source_text = ""
    st.session_state.result_area = ""
    st.session_state.quote = ""
    st.session_state.delimiter = ","
    st.session_state.keep_line_breaks = False
    st.session_state.remove_spaces = False
    st.session_state.skip_header = False
    st.session_state.wrap_in_in = True


def build_action():
    st.session_state.result_area = build_output(
        st.session_state.source_text,
        st.session_state.delimiter,
        st.session_state.quote,
        st.session_state.keep_line_breaks,
        st.session_state.remove_spaces,
        st.session_state.skip_header,
        st.session_state.wrap_in_in,
    )


def main():
    init_state()

    st.markdown(
        """
        <style>
        body { background: #f4f5e9; }
        [data-testid="stAppViewContainer"] { background: #f4f5e9; }
        .block-container { padding-top: 1.6rem; padding-bottom: 1.25rem; }
        .top-gap { margin-bottom: 1.2rem; }
        .stTextArea textarea { font-family: 'Consolas', 'SFMono-Regular', Menlo, monospace; }
        .stButton>button { height: 44px; font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Формирование строки IN для запроса")

    # Две колонки с кнопками, как в примере
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.button(
            "Очистить всё",
            type="secondary",
            use_container_width=True,
            key="clear_btn",
            on_click=clear_all,
        )
    with col3:
        render_copy_script(st.session_state.get("result_area", ""))

    st.markdown('<div class="top-gap"></div>', unsafe_allow_html=True)

    col_source, col_controls, col_output = st.columns([1.2, 0.8, 1.2])

    with col_source:
        st.markdown("**Строка - источник**", help="Вставьте столбец из Excel или любой список")
        st.text_area(
            label="Строка - источник",
            label_visibility="collapsed",
            height=420,
            placeholder="3713\n3714\n3715",
            key="source_text",
        )

    with col_controls:
        st.markdown("**Разделитель**")
        st.selectbox(
            "Разделитель",
            options=[",", ";"],
            label_visibility="collapsed",
            index=[",", ";"].index(st.session_state.delimiter) if st.session_state.delimiter in [",", ";"] else 0,
            key="delimiter",
        )

        st.markdown("**Обрамление**")
        st.text_input(
            label="Обрамление",
            label_visibility="collapsed",
            max_chars=2,
            help="Например \" или '",
            key="quote",
        )

        st.write("\n")
        st.button("➡️", use_container_width=True, key="build_btn", on_click=build_action)

        st.checkbox("Без 1 строки", key="skip_header")
        st.checkbox("Перенос строки", key="keep_line_breaks")
        st.checkbox("Удалять пробелы", key="remove_spaces")
        st.checkbox("Поместить в IN (..)", key="wrap_in_in")

    with col_output:
        st.markdown("**Строка IN**")
        st.text_area(
            label="Строка IN",
            label_visibility="collapsed",
            height=420,
            key="result_area",
        )

    if st.session_state.get("result_area"):
        st.caption("Нажмите стрелку, чтобы обновить строку после изменений")


if __name__ == "__main__":
    main()
