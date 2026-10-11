import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Hansol Inventory Valuation Analyzer',page_icon='📦',layout='wide')
st.title('📦 Hansol Inventory Valuation Analyzer')
st.caption('한솔테크닉스 연결재무제표 공시 기반 | 재고자산 평가위험 및 결산 점검 우선순위')

# 공시 연결 주석: 원 단위는 천원. 평가충당금은 절댓값으로 기록.
DATA = {
 '2024년 말': {
  '상품':(2701406,72030),'제품':(30068475,1772359),'재공품':(10041024,923091),
  '원재료':(43837872,4600335),'저장품':(142755,0),'용지':(13381893,0),'운송중 재고':(8659000,0)},
 '2025년 말': {
  '상품':(5705349,80030),'제품':(29864890,1751421),'재공품':(22326236,1767649),
  '원재료':(72096299,8403964),'저장품':(0,0),'용지':(16277893,4172603),'운송중 재고':(9604333,0)},
 '2026년 상반기 말': {
  '상품':(6587027,39240),'제품':(38873643,2025019),'재공품':(27527059,1931984),
  '원재료':(79899868,9360780),'저장품':(0,0),'용지':(16277893,4172603),'운송중 재고':(8596618,0)}
}
SOURCES = {
 '2024년 말':'2024 사업보고서(2025.03.11), 연결 주석 8. 재고자산, PDF 99쪽(인쇄 95쪽)',
 '2025년 말':'2025 사업보고서(2026.03.11), 연결 주석 7. 재고자산, PDF 102~103쪽(인쇄 98~99쪽)',
 '2026년 상반기 말':'2026 반기보고서(2026.08.13), 연결 주석 7. 재고자산, PDF 77~78쪽(인쇄 73~74쪽)'
}
PERIODS=list(DATA)
MANUFACTURING=['원재료','재공품','제품','상품']

@st.cache_data
def build_df():
 rows=[]
 for period,items in DATA.items():
  for kind,(gross,allowance) in items.items():
   rows.append({'기간':period,'재고유형':kind,'총장부금액(억원)':gross/100000,
                '평가충당금(억원)':allowance/100000,'순장부금액(억원)':(gross-allowance)/100000,
                '설정률(%)':(allowance/gross*100 if gross else 0)})
 return pd.DataFrame(rows)

df=build_df()
fmt=lambda x:f'{x:,.1f}'

t1,t2,t3,t4=st.tabs(['① 프로그램 설명','② 재고자산 현황','③ 평가위험 비교','④ 결론·실행 제언'])

with t1:
 st.header('왜 한솔테크닉스의 재고자산인가?')
 st.markdown('''한솔테크닉스는 전자부품·전장부품·EMS·태양광 모듈과 반도체 부품 등 여러 제조사업을 영위합니다. 사업별 사용 자재와 고객사 사양, 생산공정이 다르므로 원재료·재공품·제품을 구분해 평가하는 일이 중요합니다.

**분석 계기:** 2026년 상반기 연결 재고자산평가손실이 전년 동기 **약 4.9억원 → 10.1억원**으로 증가했습니다. 2026년 상반기 말 원재료 평가충당금은 **93.6억원**으로 전체 평가충당금의 약 **53.4%**를 차지합니다.

**분석 질문:** 어느 재고 유형의 평가충당금 규모와 설정률이 높고, 결산·재고관리 과정에서 어떤 항목을 먼저 점검해야 할까요?

**방법:** ① 공시 주석의 재고 유형별 금액 입력 → ② 평가충당금 설정률 및 추이 비교 → ③ 원재료 집중 분석 → ④ 실행 가능한 점검 과제 제시.

**주의:** 이 프로그램은 공개 재무제표를 이용한 *평가위험 검토 우선순위 도구*입니다. 실제 장기체화 품목, 개별 원가, 순실현가능가치, 회수가능성은 내부 자료 없이는 확인할 수 없습니다.''')
 st.info('재고자산 평가충당금 잔액의 증가액과 당기 재고자산평가손실은 동일하지 않습니다. 신규 연결편입·재고처분·환입 등의 영향이 있을 수 있습니다.')
 st.subheader('자료 출처')
 for p,s in SOURCES.items(): st.write(f'- **{p}**: {s}')

with t2:
 st.header('재고자산 유형별 잔액')
 p=st.selectbox('기준 시점',PERIODS,index=2,key='p2')
 d=df[df['기간']==p].copy()
 total=d[['총장부금액(억원)','평가충당금(억원)','순장부금액(억원)']].sum()
 c1,c2,c3=st.columns(3)
 c1.metric('평가 전 총장부금액',f"{fmt(total['총장부금액(억원)'])}억원")
 c2.metric('평가충당금',f"{fmt(total['평가충당금(억원)'])}억원")
 c3.metric('순장부금액',f"{fmt(total['순장부금액(억원)'])}억원")
 st.plotly_chart(px.bar(d.sort_values('총장부금액(억원)',ascending=False),x='재고유형',y=['총장부금액(억원)','평가충당금(억원)'],barmode='group',title='재고 유형별 총장부금액과 평가충당금'),use_container_width=True)
 st.dataframe(d[['재고유형','총장부금액(억원)','평가충당금(억원)','순장부금액(억원)','설정률(%)']].style.format({c:'{:,.2f}' for c in ['총장부금액(억원)','평가충당금(억원)','순장부금액(억원)','설정률(%)']}),use_container_width=True,hide_index=True)
 st.caption(SOURCES[p])

with t3:
 st.header('재고자산 평가위험: 규모와 설정률을 함께 비교')
 m=df[df['재고유형'].isin(MANUFACTURING)].copy()
 c1,c2=st.columns(2)
 with c1:
  st.plotly_chart(px.line(m,x='기간',y='설정률(%)',color='재고유형',markers=True,category_orders={'기간':PERIODS},title='제조 관련 재고 유형별 평가충당금 설정률'),use_container_width=True)
 with c2:
  st.plotly_chart(px.bar(m,x='기간',y='평가충당금(억원)',color='재고유형',barmode='group',category_orders={'기간':PERIODS},title='제조 관련 재고 유형별 평가충당금 규모'),use_container_width=True)
 st.subheader('2024년 말 대비 2026년 상반기 말')
 start=m[m['기간']==PERIODS[0]].set_index('재고유형')
 end=m[m['기간']==PERIODS[2]].set_index('재고유형')
 comparison=pd.DataFrame({'재고유형':MANUFACTURING})
 comparison['2024년 말 설정률(%)']=[start.loc[k,'설정률(%)'] for k in MANUFACTURING]
 comparison['2026년 상반기 설정률(%)']=[end.loc[k,'설정률(%)'] for k in MANUFACTURING]
 comparison['설정률 변화(%p)']=comparison['2026년 상반기 설정률(%)']-comparison['2024년 말 설정률(%)']
 comparison['2026년 상반기 충당금(억원)']=[end.loc[k,'평가충당금(억원)'] for k in MANUFACTURING]
 st.dataframe(comparison.style.format({c:'{:,.2f}' for c in comparison.columns if c!='재고유형'}),use_container_width=True,hide_index=True)
 st.success('원재료는 제조 관련 재고 중 2026년 상반기 말 평가충당금 규모와 설정률이 모두 가장 높고, 2024년 말 대비 설정률도 상승했습니다. **결산 검토 우선 대상으로 선정**할 근거가 있습니다.')
 st.warning('2025년 한솔오리온텍, 2026년 윌테크놀러지 등 연결범위 변동이 있습니다. 잔액 증가를 기존 사업의 평가위험 악화로 단정할 수 없습니다. 용지(부동산 관련 재고)는 제조 재고와 구분해 표시했습니다.')

with t4:
 st.header('최종 결론 및 회계·재고관리 제언')
 p='2026년 상반기 말'
 d=df[df['기간']==p].set_index('재고유형')
 raw=d.loc['원재료']; total_allow=d['평가충당금(억원)'].sum()
 c1,c2,c3=st.columns(3)
 c1.metric('원재료 평가충당금',f"{raw['평가충당금(억원)']:.1f}억원")
 c2.metric('원재료 설정률',f"{raw['설정률(%)']:.2f}%")
 c3.metric('전체 충당금 중 원재료 비중',f"{raw['평가충당금(억원)']/total_allow*100:.1f}%")
 st.markdown('''### 결론
**원재료를 재고자산 평가·결산 검증의 우선 관리 대상으로 선정합니다.** 2026년 상반기 말 원재료 평가충당금은 제조 관련 재고 중 가장 크고, 설정률도 2024년 말 대비 상승했습니다.

### 실행 과제
**1. 결산 검증 — 원재료 평가 근거 점검**  
원재료별 장부원가, 예상 사용량, 완제품 순실현가능가치 및 관련 평가 가정을 대조하고, 평가충당금 산정 근거와 변동 사유를 문서화합니다.

**2. 생산·구매 협업 — 장기 미사용 원재료 선별**  
장기 미사용 품목과 향후 생산계획에 반영되지 않은 품목을 분리해 구매·생산부서에 확인하고, 대체 사용 가능성과 추가 발주 조정 필요성을 검토합니다.

**3. 연결결산 — 비교가능성 확보**  
신규 연결편입 기업의 원재료·충당금 잔액을 구분해 기존 사업의 변화와 연결범위 변동 효과를 별도로 설명하도록 관리합니다.

**4. 월별 모니터링 — 규모와 비율 동시 확인**  
원재료 총장부금액, 평가충당금, 설정률을 함께 추적합니다. 충당금이 증가해도 원재료 규모 증가에 따른 효과인지, 설정률 변화 때문인지 구분합니다.''')
 st.divider()
 st.subheader('재고자산평가손실과 충당금 잔액은 구분')
 loss=pd.DataFrame({'기간':['2025년 상반기','2026년 상반기'],'재고자산평가손실(억원)':[4.89071,10.09576]})
 st.plotly_chart(px.bar(loss,x='기간',y='재고자산평가손실(억원)',text_auto='.2f',title='연결 재고자산평가손실(반기 누적)'),use_container_width=True)
 st.caption('2026년 반기보고서 연결 주석 7: 전반기 489,071천원, 당반기 1,009,576천원. 품목별 손실액은 공시되지 않았으므로 이를 원재료 손실로 단정하지 않습니다.')
 st.info('이 프로그램은 공시자료로 확인되는 위험의 **점검 순서**를 제안합니다. 실제 품목별 체화 여부나 향후 절감액을 계산하거나 단정하지 않습니다.')
