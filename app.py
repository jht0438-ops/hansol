import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Hansol Segment Profit Navigator", page_icon="📊", layout="wide")
st.title("Hansol Segment Profit Navigator")
st.caption("한솔테크닉스 | 사업부문별 손익·비용 변화 분석 | 생성형 AI를 활용해 구현한 Python·Streamlit 앱")

SEGMENTS = ["전자부품", "제품·조립", "반도체"]
# 단위: 천원. 공시 원문 수치를 그대로 기재하며 화면에서는 억원으로 환산.
DATA = {
    "2023": {
        "revenue": [669364587, 509417268, 123897248],
        "profit": [30151650, 16897144, 1888624],
        "da_tangible": [14002195, 9463019, 6781926],
        "da_intangible": [492267, 1717117, 6783556],
        "da_rou": [1723272, 66175, 403634],
        "elimination": None,
        "consolidated_revenue": None,
        "source": "2023 사업보고서(2024.03.13), 연결 주석 4. 부문손익, PDF 111쪽",
    },
    "2024": {
        "revenue": [649905941, 392439543, 157137657],
        "profit": [14147873, 2430976, 16775735],
        "da_tangible": [12470701, 9220586, 7555316],
        "da_intangible": [616301, 870, 7065847],
        "da_rou": [2665229, 69334, 579187],
        "elimination": None,
        "consolidated_revenue": None,
        "source": "2024 사업보고서(2025.03.11), 연결 주석 4. 부문손익, PDF 95쪽",
    },
    "2025": {
        "revenue": [1055381701, 414206052, 198830230],
        "profit": [-20009869, 15591298, 24834261],
        "da_tangible": [13154107, 5656996, 7892130],
        "da_intangible": [3254955, 0, 7124892],
        "da_rou": [2731462, 72097, 451884],
        "elimination": -415993222,
        "consolidated_revenue": 1252424761,
        "source": "2025 사업보고서(2026.03.11), 연결 주석 4. 부문손익, PDF 98쪽",
    },
    "2025 상반기": {
        "revenue": [567892699, 195971228, 95872556],
        "profit": [6808911, 7435096, 17847507],
        "da_tangible": [6628136, 2643780, 3790990],
        "da_intangible": [333124, 0, 3552903],
        "da_rou": [1312101, 35896, 232757],
        "elimination": -228409577,
        "consolidated_revenue": 631326906,
        "source": "2026 반기보고서(2026.08.13), 연결 주석 4. 부문손익, PDF 73~74쪽 전반기",
    },
    "2026 상반기": {
        "revenue": [478235048, 238845596, 102909671],
        "profit": [9248572, 9612558, 9478993],
        "da_tangible": [5838307, 2842330, 4378175],
        "da_intangible": [2809774, 10308, 3619528],
        "da_rou": [1535559, 51229, 239443],
        "elimination": -168924815,
        "consolidated_revenue": 651065500,
        "source": "2026 반기보고서(2026.08.13), 연결 주석 4. 부문손익, PDF 73~74쪽 당반기",
    },
}
ORDER = ["2023", "2024", "2025", "2025 상반기", "2026 상반기"]
def billion(x): return x / 100000.0  # 천원 -> 억원
def frame(period):
    d=DATA[period]
    f=pd.DataFrame({"부문":SEGMENTS,"매출액(억원)":[billion(x) for x in d["revenue"]],
        "영업이익(억원)":[billion(x) for x in d["profit"]],
        "유형자산 감가상각비(억원)":[billion(x) for x in d["da_tangible"]],
        "무형자산상각비(억원)":[billion(x) for x in d["da_intangible"]],
        "사용권자산 감가상각비(억원)":[billion(x) for x in d["da_rou"]]})
    f["영업이익률(%)"]=f["영업이익(억원)"]/f["매출액(억원)"]*100
    f["상각비 합계(억원)"]=f.iloc[:,3:6].sum(axis=1)
    return f
def fmt(x): return f"{x:,.1f}"
tabs=st.tabs(["① 프로그램 설명","② 사업부문 손익 추이","③ 영업이익 변동 분해","④ 상각비·수익성 점검","⑤ 결산 검증·자료 출처"])
with tabs[0]:
    st.header("왜 이 프로그램을 만들었나요?")
    st.write("""한솔테크닉스는 전자부품·제품조립·반도체 사업을 운영합니다. 2025년에는 반도체 부문의
    영업이익이 확대된 반면 전자부품 부문은 적자로 전환했습니다. 2026년 상반기에는 반도체 매출이
    증가했음에도 반도체 영업이익이 감소했습니다. 이러한 **부문별 상반된 흐름**이 전사 영업이익에
    어떤 영향을 주는지, 어떤 비용 항목을 추가 검증해야 하는지 확인하고자 프로그램을 만들었습니다.""")
    st.subheader("어떻게 분석하나요?")
    st.write("""① 공시된 연결재무제표 주석의 3개 영업부문 매출액·영업이익을 기간별로 정리합니다.
    ② 2025년 상반기와 2026년 상반기를 동일 기간으로 비교합니다.
    ③ 부문별 영업이익 증감을 **매출 규모 효과와 영업이익률 효과로 산술 분해**합니다.
    ④ 감가상각비·무형자산상각비 변동을 점검하고 결산 검증 질문을 제시합니다.""")
    st.info("중요: 부문 매출에는 내부거래가 포함될 수 있습니다. 연결 매출액과 직접 같지 않으므로 내부거래 제거를 구분합니다. 영업이익률 효과는 회계적 산술 분해이지, 가격·원가의 인과관계를 입증하지 않습니다.")
    st.subheader("이 프로그램을 통해 얻는 결론")
    st.write("매출 성장과 이익 성장을 구분하고, 손익 변동이 큰 사업부문 및 확인이 필요한 비용 항목을 식별하여 결산·외부감사 자료 검토의 우선순위를 제시합니다.")
    st.caption("모든 분석은 공개된 공시자료 기반이며 내부 원장, 제품별 표준원가, 원가배부 기준은 포함되지 않습니다.")
with tabs[1]:
    st.header("사업부문별 손익 추이")
    period=st.selectbox("조회 기간",ORDER,index=4)
    f=frame(period)
    c1,c2,c3=st.columns(3)
    c1.metric("부문 매출 합계(내부거래 포함)",f"{f['매출액(억원)'].sum():,.1f}억원")
    c2.metric("부문 영업이익 합계",f"{f['영업이익(억원)'].sum():,.1f}억원")
    c3.metric("반도체 영업이익",f"{f.loc[f['부문']=='반도체','영업이익(억원)'].iloc[0]:,.1f}억원")
    st.dataframe(f[["부문","매출액(억원)","영업이익(억원)","영업이익률(%)"]].style.format(precision=2),use_container_width=True,hide_index=True)
    fig=px.bar(f,x="부문",y="영업이익(억원)",color="부문",text_auto=".1f",title=f"{period} 사업부문별 영업이익")
    fig.add_hline(y=0,line_color="gray")
    st.plotly_chart(fig,use_container_width=True)
    d=DATA[period]
    if d["elimination"] is not None:
        st.subheader("부문 매출과 연결 매출 대사")
        st.write(f"부문 매출 합계 **{fmt(f['매출액(억원)'].sum())}억원** + 내부거래 등 제거 **{fmt(billion(d['elimination']))}억원** = 연결 매출 **{fmt(billion(d['consolidated_revenue']))}억원**")
    else:
        st.caption("해당 기간의 매출 제거·연결매출 대사 데이터는 이 앱에 입력하지 않았습니다.")
    st.caption(d["source"])
with tabs[2]:
    st.header("전년 동기 영업이익 변동 분해")
    st.write("비교기간: **2025년 상반기 → 2026년 상반기** (연간 실적과 반기 실적을 직접 비교하지 않음)")
    old=frame("2025 상반기").set_index("부문")
    new=frame("2026 상반기").set_index("부문")
    bridge=pd.DataFrame(index=SEGMENTS)
    bridge["2025 H1 영업이익"]=old["영업이익(억원)"]
    bridge["2026 H1 영업이익"]=new["영업이익(억원)"]
    bridge["영업이익 증감"]=bridge["2026 H1 영업이익"]-bridge["2025 H1 영업이익"]
    bridge["매출 증감"]=new["매출액(억원)"]-old["매출액(억원)"]
    bridge["영업이익률 변화(%p)"]=new["영업이익률(%)"]-old["영업이익률(%)"]
    st.dataframe(bridge.style.format("{:,.2f}"),use_container_width=True)
    st.plotly_chart(px.bar(bridge.reset_index().rename(columns={"index":"부문"}),x="부문",y="영업이익 증감",color="부문",text_auto=".1f",title="전년 동기 대비 영업이익 증감(억원)"),use_container_width=True)
    st.subheader("매출 규모 효과 vs 이익률 효과 (산술적 분해)")
    st.latex(r"\Delta OP = (R_1-R_0)\times m_0 + R_1\times(m_1-m_0)")
    st.caption("R=부문 매출, m=부문 영업이익률. '매출 규모 효과'는 전기 이익률 유지 가정, '이익률 효과'는 그 나머지입니다. 실제 원가 상승, 판가, 제품 믹스 등의 원인을 구분한 결과가 아닙니다.")
    decomp=pd.DataFrame(index=SEGMENTS)
    decomp["매출 규모 효과(억원)"]=(new["매출액(억원)"]-old["매출액(억원)"])*old["영업이익률(%)"]/100
    decomp["이익률 효과(억원)"]=new["매출액(억원)"]*(new["영업이익률(%)"]-old["영업이익률(%)"])/100
    decomp["합계(억원)"]=decomp.sum(axis=1)
    st.dataframe(decomp.style.format("{:,.2f}"),use_container_width=True)
    st.plotly_chart(px.bar(decomp.reset_index().rename(columns={"index":"부문"}),x="부문",y=["매출 규모 효과(억원)","이익률 효과(억원)"],barmode="relative",title="영업이익 변동의 산술적 구성"),use_container_width=True)
    st.success(f"전사 부문 영업이익 변화: {bridge['영업이익 증감'].sum():,.1f}억원. 반도체 부문의 변화 {bridge.loc['반도체','영업이익 증감']:,.1f}억원이 가장 큰 감소 요인으로 관찰됩니다.")
with tabs[3]:
    st.header("비용 구조와 수익성 점검")
    st.write("반도체 부문을 중심으로 공시된 상각비 변동을 확인합니다. 상각비는 영업이익에 영향을 주는 비용이지만, **모든 상각비가 당기 매출원가·판관비에 동일하게 반영되는 것은 아닐 수 있으므로** 단순히 더해 영업이익 원인을 확정하지 않습니다.")
    seg=st.selectbox("부문 선택",SEGMENTS,index=2)
    old=frame("2025 상반기").set_index("부문").loc[seg]
    new=frame("2026 상반기").set_index("부문").loc[seg]
    cols=["유형자산 감가상각비(억원)","무형자산상각비(억원)","사용권자산 감가상각비(억원)"]
    cost=pd.DataFrame({"비용 항목":cols,"2025 상반기":[old[c] for c in cols],"2026 상반기":[new[c] for c in cols]})
    cost["증감"]=cost["2026 상반기"]-cost["2025 상반기"]
    st.dataframe(cost.style.format({"2025 상반기":"{:,.2f}","2026 상반기":"{:,.2f}","증감":"{:+,.2f}"}),use_container_width=True,hide_index=True)
    st.plotly_chart(px.bar(cost,x="비용 항목",y=["2025 상반기","2026 상반기"],barmode="group",title=f"{seg} 상각비 비교"),use_container_width=True)
    st.markdown("**추가 확인이 필요한 자료**: 제품별 원가 및 수량, 원재료 구매가격, 제조경비, 인건비, 가동률, 판관비, 사업결합에 따른 연결범위 변동.")
    st.warning("부문별 상각비만으로 영업이익 변동의 실제 원인을 규명할 수 없습니다. '검토할 계정'을 식별하는 데 사용하세요.")
with tabs[4]:
    st.header("결산 검증 체크리스트 및 출처")
    st.write("회계 담당자의 결산 지원과 감사 대응 관점에서, 부문 손익을 확인할 때 필요한 검증 항목입니다.")
    for item in [
        "사업부문별 매출 집계액과 부문 간 내부거래 제거액이 연결 매출과 일치하는가?",
        "부문별 영업이익 합계와 연결 영업이익이 일치하는가? 조정사항은 무엇인가?",
        "전기 대비 부문 분류나 연결대상 회사가 달라졌는가?",
        "영업이익률이 급변한 부문의 원가·판관비 계정별 증감 사유가 증빙과 일치하는가?",
        "감가상각비·무형자산상각비는 자산대장과 결산 전표에 일치하는가?",
        "반기 비교는 동일한 기간·동일한 연결기준으로 수행했는가?",
    ]:
        st.checkbox(item)
    st.subheader("원문 수치 자동 점검")
    for k in ORDER:
        d=DATA[k]
        prof_sum=sum(d["profit"])
        st.write(f"**{k}** — 부문 영업이익 합계 {fmt(billion(prof_sum))}억원")
        if d["consolidated_revenue"] is not None:
            diff=sum(d["revenue"])+d["elimination"]-d["consolidated_revenue"]
            st.write(f"매출 연결 대사 차이: {diff:,}천원 " + ("✅" if diff==0 else "⚠️ 확인 필요"))
    st.subheader("공시자료 출처")
    for k in ORDER: st.write(f"- **{k}**: {DATA[k]['source']}")
    st.info("본 앱은 공시 원문에 기재된 부문손익·상각비를 정리한 분석 도구이며, 회계감사나 실제 결산을 대체하지 않습니다.")
