import json
import os
import streamlit as st
import storage

# --------------------------------------------------------------------------
# Cấu hình trang
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Đánh giá tiềm năng NST",
    page_icon="📊",
    layout="centered",
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


@st.cache_data
def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config(CONFIG_PATH)

# --------------------------------------------------------------------------
# CSS tuỳ chỉnh
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .group-header {
        padding: 10px 16px;
        border-radius: 8px;
        color: white;
        font-weight: 700;
        font-size: 16px;
        margin-top: 18px;
        margin-bottom: 8px;
    }
    .question-box {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background-color: #fafafa;
    }
    .question-text { font-weight: 600; font-size: 15px; margin-bottom: 2px; }
    .question-note { font-size: 12px; color: #d9770d; font-style: italic; margin-bottom: 4px; }
    .scale-hint { font-size: 12px; color: #888; margin-top: 2px; }
    div[role="radiogroup"] > label {
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 4px 10px;
        margin-right: 4px;
    }
    .result-banner { padding: 20px; border-radius: 10px; color: white; text-align: center; margin-top: 14px; }
    .result-banner h2, .result-banner h3 { margin: 4px 0; color: white; }
    .warning-box {
        border: 1px solid #f5c26b;
        background-color: #fff8ec;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 14px;
    }
    .progress-label { font-size: 13px; color: #555; margin-bottom: -6px; }
    .team-card {
        border: 2px solid #eee;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(config.get("app_title", "Đánh giá tiềm năng"))
if config.get("app_subtitle"):
    st.caption(config["app_subtitle"])

st.divider()

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "selected_team" not in st.session_state:
    st.session_state.selected_team = None


def reset_all():
    st.session_state.answers = {}
    st.session_state.submitted = False
    st.session_state.tiktok_id = ""
    st.session_state.agency = ""
    st.session_state.evaluator_name = ""


# --------------------------------------------------------------------------
# Bước 1 — Chọn team
# --------------------------------------------------------------------------
st.markdown("### 🌍 Chọn Team")
team_keys = list(config["teams"].keys())
team_option_labels = [config["teams"][k]["label"] for k in team_keys]

current_index = team_keys.index(st.session_state.selected_team) if st.session_state.selected_team in team_keys else None

chosen_label = st.radio(
    "Team",
    options=team_option_labels,
    index=current_index,
    horizontal=True,
    label_visibility="collapsed",
    key="team_radio",
)

new_team = team_keys[team_option_labels.index(chosen_label)] if chosen_label else None

# Nếu người dùng đổi sang team khác -> xoá câu trả lời cũ (khác bộ câu hỏi)
if new_team != st.session_state.selected_team:
    st.session_state.answers = {}
    st.session_state.submitted = False
    st.session_state.selected_team = new_team

if not st.session_state.selected_team:
    st.info("👆 Vui lòng chọn Team để hiện bộ câu hỏi tương ứng.")
    st.stop()

team_id = st.session_state.selected_team
team_cfg = config["teams"][team_id]
st.caption(team_cfg.get("description", ""))

st.divider()

# --------------------------------------------------------------------------
# Bước 2 — Thông tin định danh
# --------------------------------------------------------------------------
st.markdown("### 🧾 Thông tin chung")
info_col1, info_col2, info_col3 = st.columns(3)
with info_col1:
    tiktok_id = st.text_input("ID / Tên TikToker *", key="tiktok_id", placeholder="vd: @username")
with info_col2:
    agency = st.text_input("Agency *", key="agency", placeholder="vd: ABC Media")
with info_col3:
    evaluator_name = st.text_input("Người chấm *", key="evaluator_name", placeholder="Tên người trả lời")

st.divider()

# --------------------------------------------------------------------------
# Bước 3 — Render câu hỏi theo team đã chọn
# --------------------------------------------------------------------------
groups = team_cfg["groups"]
total_questions = sum(len(g["questions"]) for g in groups)
group_scores = {}

for group in groups:
    color = group.get("color", "#4a90d9")
    st.markdown(
        f'<div class="group-header" style="background-color:{color};">{group["title"]}</div>',
        unsafe_allow_html=True,
    )

    group_score = 0
    group_max = len(group["questions"]) * 5

    for q in group["questions"]:
        qid = f'{group["id"]}_{q["id"]}'
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="question-text">{q["id"]}. {q["text"]}</div>', unsafe_allow_html=True)
        if q.get("note"):
            st.markdown(f'<div class="question-note">{q["note"]}</div>', unsafe_allow_html=True)

        options = [1, 2, 3, 4, 5]
        current = st.session_state.answers.get(qid, None)

        selected = st.radio(
            label="",
            options=options,
            index=options.index(current) if current in options else None,
            horizontal=True,
            key=f"radio_{team_id}_{qid}",
            label_visibility="collapsed",
        )

        if selected is not None:
            st.session_state.answers[qid] = selected
            group_score += selected

        hint_parts = [f"**{lvl}** = {q['labels'][str(lvl)]}" for lvl in options]
        st.markdown(f'<div class="scale-hint">{" &nbsp;|&nbsp; ".join(hint_parts)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    group_scores[group["id"]] = group_score
    st.markdown(
        f'<div class="progress-label">{group["title"].split("—")[0].strip()}: {group_score}/{group_max}</div>',
        unsafe_allow_html=True,
    )
    st.progress(group_score / group_max if group_max else 0)

st.divider()

# --------------------------------------------------------------------------
# Tổng tiến độ + nút hành động
# --------------------------------------------------------------------------
answered_count = len(st.session_state.answers)
total_score = sum(st.session_state.answers.values())
total_max = total_questions * 5

goal_text = team_cfg.get("progress_goal_text", "nhận kết quả")
st.markdown(
    f'<div class="progress-label">Đã chấm {answered_count}/{total_questions} câu. '
    f'Hoàn thành cả {total_questions} câu để {goal_text}.</div>',
    unsafe_allow_html=True,
)
st.progress(answered_count / total_questions if total_questions else 0)

col1, col2 = st.columns(2)
with col1:
    submit_clicked = st.button(team_cfg.get("submit_label", "✅ Gửi kết quả"), use_container_width=True, type="primary")
with col2:
    st.button("🔄 Chấm lại từ đầu", use_container_width=True, on_click=reset_all)

# --------------------------------------------------------------------------
# Hàm phân loại — kiểu 1: cộng điểm theo dải (sum_bands) — dùng cho Team US
# --------------------------------------------------------------------------
def classify_sum_bands(total, bands):
    for band in bands:
        if band["min"] <= total <= band["max"]:
            return band
    return None


# --------------------------------------------------------------------------
# Hàm phân loại — kiểu 2: phân tích theo tuyến (lane_analysis) — dùng cho Team VN
# --------------------------------------------------------------------------
def classify_lane_analysis(scores, lane_cfg):
    labels = lane_cfg["lane_labels"]
    priority = lane_cfg["lane_priority"]

    sorted_lanes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_id, top_score = sorted_lanes[0]
    second_id, second_score = sorted_lanes[1]
    gap = top_score - second_score

    all_low = all(v < lane_cfg["foundation_missing_max"] for v in scores.values())

    if all_low:
        fm = lane_cfg["foundation_missing"]
        result = {"label": fm["label"], "color": fm["color"], "desc": fm["desc"]}
    elif top_score >= lane_cfg["clear_niche_min_score"] and gap >= lane_cfg["clear_niche_min_gap"]:
        cn = lane_cfg["clear_niche"]
        desc = cn["desc_template"].format(lane=labels[top_id])
        result = {"label": cn["label"], "color": cn["color"], "desc": desc}
    elif gap <= lane_cfg["dual_niche_max_gap"]:
        dn = lane_cfg["dual_niche"]
        primary = min([top_id, second_id], key=lambda g: priority.index(g))
        secondary = second_id if primary == top_id else top_id
        desc = dn["desc_template"].format(primary=labels[primary], secondary=labels[secondary])
        result = {"label": dn["label"], "color": dn["color"], "desc": desc}
    else:
        fb = lane_cfg["fallback"]
        result = {"label": fb["label"], "color": fb["color"], "desc": fb["desc"]}

    # Cảnh báo bổ sung (không loại trừ kết luận chính)
    warning_msgs = []
    for w in lane_cfg.get("warnings", []):
        gid = w["group_id"]
        qid = f'{gid}_{w["check_question_id"]}'
        group_total = scores.get(gid)
        q_score = st.session_state.answers.get(qid)
        if (
            group_total is not None
            and group_total >= lane_cfg.get("high_group_threshold", 18)
            and q_score is not None
            and q_score <= w["threshold"]
        ):
            warning_msgs.append(w["message"])

    return result, warning_msgs, {labels[k]: v for k, v in scores.items()}


# --------------------------------------------------------------------------
# Xử lý khi bấm Gửi
# --------------------------------------------------------------------------
if submit_clicked:
    missing_info = [
        label for label, val in [
            ("ID/Tên TikToker", tiktok_id),
            ("Agency", agency),
            ("Người chấm", evaluator_name),
        ] if not val.strip()
    ]
    if missing_info:
        st.warning("Vui lòng điền đầy đủ thông tin chung: " + ", ".join(missing_info) + ".")
    elif answered_count < total_questions:
        st.warning(f"Vui lòng hoàn thành cả {total_questions} câu trước khi gửi kết quả. "
                    f"Còn thiếu {total_questions - answered_count} câu.")
    else:
        st.session_state.submitted = True

        record = {
            "Thời gian": storage.now_str(),
            "Team": team_id,
            "ID_TikToker": tiktok_id.strip(),
            "Agency": agency.strip(),
            "Nguoi_cham": evaluator_name.strip(),
        }
        for group in groups:
            for q in group["questions"]:
                qid = f'{group["id"]}_{q["id"]}'
                record[qid] = st.session_state.answers.get(qid)

        if team_cfg["classification_type"] == "sum_bands":
            matched = classify_sum_bands(total_score, team_cfg["classification"]["bands"])
            record["Tong_diem"] = total_score
            record["Ket_luan"] = matched["label"] if matched else ""
            record["Ket_luan_chi_tiet"] = matched["desc"] if matched else ""
            record["Canh_bao"] = ""
            st.session_state.last_result = {"type": "sum_bands", "matched": matched}
        else:
            for gid, score in group_scores.items():
                lane_name = team_cfg["lane_analysis"]["lane_labels"][gid]
                record[f"Diem_{lane_name}"] = score
            result, warnings_list, lane_scores_named = classify_lane_analysis(
                group_scores, team_cfg["lane_analysis"]
            )
            record["Ket_luan"] = result["label"]
            record["Ket_luan_chi_tiet"] = result["desc"]
            record["Canh_bao"] = " | ".join(warnings_list)
            st.session_state.last_result = {
                "type": "lane_analysis",
                "result": result,
                "warnings": warnings_list,
                "lane_scores": lane_scores_named,
            }

        df_all, synced, sync_error = storage.append_record(record)
        if synced:
            st.toast("Đã lưu vào kho dữ liệu (local + Hugging Face Dataset) ✅", icon="✅")
        else:
            st.toast("Đã lưu vào kho dữ liệu local ✅", icon="✅")
            if sync_error:
                st.caption(f"⚠️ Không đồng bộ được lên Hugging Face Dataset: {sync_error}")

# --------------------------------------------------------------------------
# Hiển thị kết quả
# --------------------------------------------------------------------------
if st.session_state.submitted and st.session_state.get("last_result"):
    last = st.session_state.last_result
    identity_line = f"<b>{tiktok_id}</b> &nbsp;|&nbsp; Agency: {agency} &nbsp;|&nbsp; Người chấm: {evaluator_name}"

    if last["type"] == "sum_bands":
        matched = last["matched"]
        if matched:
            st.markdown(
                f"""
                <div class="result-banner" style="background-color:{matched['color']};">
                    <p style="margin:0 0 6px 0;">{identity_line}</p>
                    <h2>Tổng điểm: {total_score}/{total_max}</h2>
                    <h3>{matched['label']}</h3>
                    <p>{matched['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info(f"Tổng điểm: {total_score}/{total_max} — chưa khớp dải phân loại nào, kiểm tra lại config.json.")

    else:
        result = last["result"]
        lane_scores = last["lane_scores"]
        scores_line = " &nbsp;|&nbsp; ".join(f"{name}: {score}/25" for name, score in lane_scores.items())
        st.markdown(
            f"""
            <div class="result-banner" style="background-color:{result['color']};">
                <p style="margin:0 0 6px 0;">{identity_line}</p>
                <p style="margin:0 0 8px 0; font-size:14px;">{scores_line}</p>
                <h3>{result['label']}</h3>
                <p>{result['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for w in last["warnings"]:
            st.markdown(f'<div class="warning-box">{w}</div>', unsafe_allow_html=True)

    with st.expander("📋 Xem chi tiết từng câu trả lời"):
        for group in groups:
            st.markdown(f"**{group['title']}**")
            rows = []
            for q in group["questions"]:
                qid = f'{group["id"]}_{q["id"]}'
                val = st.session_state.answers.get(qid)
                rows.append({
                    "Câu hỏi": f'{q["id"]}. {q["text"]}',
                    "Điểm": val,
                    "Ý nghĩa": q["labels"][str(val)] if val else "",
                })
            st.table(rows)

# --------------------------------------------------------------------------
# Bảng "Cách đọc điểm" tham khảo cho Team VN
# --------------------------------------------------------------------------
if team_id == "VN":
    with st.expander("📖 Cách đọc điểm — Team VN"):
        st.markdown(
            """
            | Tình huống điểm | Kết luận & hành động |
            |---|---|
            | Một tuyến ≥ 18 điểm và cách tuyến thứ hai ≥ 4 điểm | **Ngách rõ nét**: Kích hoạt ngay Playbook chuyên sâu của tuyến đó. Không thử nghiệm dàn trải. |
            | Hai tuyến chênh nhau ≤ 3 điểm | **Ngách kép**: Chọn tuyến chi phí vận hành thấp hơn làm chính (Ưu tiên: NPC > Beauty > Music). Tuyến còn lại là "gia vị" (1 buổi/tuần). |
            | Cả 3 tuyến < 12 điểm | **Thiếu nền tảng**: Đưa vào chuỗi NPC Basic (2 tuần) để rèn kỷ luật, sau đó đánh giá lại. |
            | Nhóm B (Music) cao nhưng B5 ≤ 3 | **Cảnh báo thiếu kỷ luật**: Chưa vội đẩy vào ngách Music. |
            | Nhóm C (Beauty) cao nhưng C4 ≤ 3 | **Chệch trọng tâm**: Đúng ngách Beauty nhưng thiếu Fan-service, cần bắt đầu từ Camp 2. |
            """
        )

st.divider()

# --------------------------------------------------------------------------
# Kho dữ liệu
# --------------------------------------------------------------------------
with st.expander("🗂️ Kho dữ liệu — toàn bộ kết quả đã chấm"):
    df_store = storage.load_all()
    if df_store.empty:
        st.info("Chưa có kết quả nào được lưu.")
    else:
        st.dataframe(df_store, use_container_width=True)
        st.download_button(
            label="⬇️ Tải toàn bộ kho dữ liệu (CSV)",
            data=df_store.to_csv(index=False).encode("utf-8-sig"),
            file_name="nst_scoring_results.csv",
            mime="text/csv",
        )
    if storage.HF_TOKEN and storage.HF_DATASET_REPO:
        st.caption(f"🔄 Đang đồng bộ vào Hugging Face Dataset: `{storage.HF_DATASET_REPO}`")
    else:
        st.caption("ℹ️ Chưa cấu hình đồng bộ lên Hugging Face Dataset (dữ liệu chỉ lưu local — "
                     "xem hướng dẫn trong README.md để bật lưu trữ vĩnh viễn, miễn phí).")

st.divider()
st.caption("Ứng dụng chấm điểm nội bộ — chỉnh sửa câu hỏi / thang điểm / logic đánh giá trong file config.json, không cần sửa code.")
