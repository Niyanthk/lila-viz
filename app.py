import os, gdown, zipfile
if not os.path.exists("player_data"):
    import streamlit as st
    st.info("⏳ Downloading data, please wait 1 minute...")
    gdown.download("https://drive.google.com/uc?id=1kJjWiiTdqbOyYB8fhsdIgmrkWX_Nb-X2", "player_data.zip", quiet=False)
    with zipfile.ZipFile("player_data.zip", "r") as z:
        z.extractall(".")
    st.rerun()
import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from scipy.ndimage import gaussian_filter
import os, glob

st.set_page_config(page_title="LILA BLACK Visualizer", layout="wide", page_icon="🎮")

MAP_CONFIG = {
    "AmbroseValley": {"scale":900,  "origin_x":-370, "origin_z":-473, "minimap":"player_data/minimaps/AmbroseValley_Minimap.png"},
    "GrandRift":     {"scale":581,  "origin_x":-290, "origin_z":-290, "minimap":"player_data/minimaps/GrandRift_Minimap.png"},
    "Lockdown":      {"scale":1000, "origin_x":-500, "origin_z":-500, "minimap":"player_data/minimaps/Lockdown_Minimap.jpg"},
}
EVENT_COLORS = {"Position":"#4CAF50","BotPosition":"#8BC34A","Kill":"#F44336","Killed":"#E91E63","BotKill":"#FF5722","BotKilled":"#FF9800","KilledByStorm":"#9C27B0","Loot":"#2196F3"}
EVENT_SYMBOLS = {"Kill":"star","Killed":"x","BotKill":"triangle-up","BotKilled":"triangle-down","KilledByStorm":"diamond","Loot":"circle"}

@st.cache_data
def load_data():
    frames=[]
    for folder in sorted(glob.glob("player_data/February_*")):
        date=os.path.basename(folder)
        for f in os.listdir(folder):
            try:
                df=pq.read_table(os.path.join(folder,f)).to_pandas()
                df["date"]=date
                frames.append(df)
            except: continue
    if not frames: return pd.DataFrame()
    data=pd.concat(frames,ignore_index=True)
    data["event"]=data["event"].apply(lambda e: e.decode("utf-8") if isinstance(e,bytes) else str(e))
    data["is_bot"]=data["user_id"].apply(lambda u: str(u).isdigit())
    def px_coords(row):
        try:
            c=MAP_CONFIG[row["map_id"]]
            return pd.Series({"px":(row["x"]-c["origin_x"])/c["scale"]*1024,"py":(1-(row["z"]-c["origin_z"])/c["scale"])*1024})
        except: return pd.Series({"px":np.nan,"py":np.nan})
    data=pd.concat([data,data.apply(px_coords,axis=1)],axis=1)
    data["ts_ms"]=pd.to_numeric(data["ts"],errors="coerce")
    return data.sort_values(["match_id","ts_ms"])

data=load_data()
st.sidebar.title("🎮 LILA BLACK")
selected_map=st.sidebar.selectbox("Map",sorted(data["map_id"].dropna().unique()))
d=data[data["map_id"]==selected_map]
dates=sorted(d["date"].unique())
sel_dates=st.sidebar.multiselect("Date",dates,default=dates)
d=d[d["date"].isin(sel_dates)]
matches=["ALL"]+sorted(d["match_id"].dropna().unique().tolist())
sel_match=st.sidebar.selectbox("Match",matches)
if sel_match!="ALL": d=d[d["match_id"]==sel_match]
ptype=st.sidebar.radio("Players",["All","Humans Only","Bots Only"])
if ptype=="Humans Only": d=d[~d["is_bot"]]
elif ptype=="Bots Only": d=d[d["is_bot"]]
evts=sorted(d["event"].unique())
sel_evts=st.sidebar.multiselect("Events",evts,default=evts)
d=d[d["event"].isin(sel_evts)]
st.sidebar.metric("Events",f"{len(d):,}")
st.sidebar.metric("Matches",d["match_id"].nunique())

def base_fig(map_name):
    fig=go.Figure()
    cfg=MAP_CONFIG[map_name]
    if os.path.exists(cfg["minimap"]):
        img=Image.open(cfg["minimap"]).resize((1024,1024))
        fig.add_layout_image(dict(source=img,xref="x",yref="y",x=0,y=0,sizex=1024,sizey=1024,sizing="stretch",opacity=0.85,layer="below"))
    fig.update_xaxes(range=[0,1024],showgrid=False,visible=False)
    fig.update_yaxes(range=[1024,0],showgrid=False,visible=False,scaleanchor="x")
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="#1a1a2e",plot_bgcolor="#1a1a2e",height=620)
    return fig

tab1,tab2,tab3,tab4=st.tabs(["🗺️ Player Paths","🔥 Heatmaps","⏯️ Playback","📊 Stats"])

with tab1:
    fig=base_fig(selected_map)
    pos=d[d["event"].isin({"Position","BotPosition"})].dropna(subset=["px","py"])
    for uid,g in pos.groupby("user_id"):
        fig.add_trace(go.Scatter(x=g["px"],y=g["py"],mode="lines",line=dict(color="rgba(139,195,74,0.3)" if g["is_bot"].iloc[0] else "rgba(76,175,80,0.5)",width=1),showlegend=False,hoverinfo="skip"))
    act=d[~d["event"].isin({"Position","BotPosition"})].dropna(subset=["px","py"])
    for evt,g in act.groupby("event"):
        fig.add_trace(go.Scatter(x=g["px"],y=g["py"],mode="markers",marker=dict(color=EVENT_COLORS.get(evt,"#fff"),size=8,symbol=EVENT_SYMBOLS.get(evt,"circle"),line=dict(width=1,color="white")),name=evt))
    st.plotly_chart(fig,use_container_width=True)

with tab2:
    hm=st.radio("Heatmap Type",["Kill Zones","Death Zones","Traffic","Storm Deaths","Loot"],horizontal=True)
    emap={"Kill Zones":["Kill","BotKill"],"Death Zones":["Killed","BotKilled"],"Traffic":["Position","BotPosition"],"Storm Deaths":["KilledByStorm"],"Loot":["Loot"]}
    hd=data[data["map_id"]==selected_map][data["event"].isin(emap[hm])].dropna(subset=["px","py"])
    if not hd.empty:
        H,xe,ye=np.histogram2d(hd["px"],hd["py"],bins=64,range=[[0,1024],[0,1024]])
        fig2=base_fig(selected_map)
        fig2.add_trace(go.Heatmap(z=gaussian_filter(H.T,sigma=2),x=np.linspace(0,1024,64),y=np.linspace(0,1024,64),colorscale="Hot",opacity=0.6,showscale=True))
        st.plotly_chart(fig2,use_container_width=True)

with tab3:
    if sel_match=="ALL":
        st.info("Select a specific match in the sidebar to enable playback.")
    else:
        md=d.dropna(subset=["px","py","ts_ms"]).sort_values("ts_ms")
        ts_min,ts_max=int(md["ts_ms"].min()),int(md["ts_ms"].max())
        rng=st.slider("Timeline",ts_min,ts_max,(ts_min,ts_min+(ts_max-ts_min)//4),step=max(1,(ts_max-ts_min)//200))
        w=md[(md["ts_ms"]>=rng[0])&(md["ts_ms"]<=rng[1])]
        fig3=base_fig(selected_map)
        for uid,g in w[w["event"].isin({"Position","BotPosition"})].groupby("user_id"):
            fig3.add_trace(go.Scatter(x=g["px"],y=g["py"],mode="lines+markers",line=dict(width=1.5),marker=dict(size=3),name=str(uid)[:8]))
        for evt,g in w[~w["event"].isin({"Position","BotPosition"})].groupby("event"):
            fig3.add_trace(go.Scatter(x=g["px"],y=g["py"],mode="markers",marker=dict(color=EVENT_COLORS.get(evt,"#fff"),size=10,symbol=EVENT_SYMBOLS.get(evt,"circle")),name=evt))
        st.plotly_chart(fig3,use_container_width=True)

with tab4:
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Events",f"{len(d):,}")
    c2.metric("Matches",d["match_id"].nunique())
    c3.metric("Humans",d[~d["is_bot"]]["user_id"].nunique())
    c4.metric("Bots",d[d["is_bot"]]["user_id"].nunique())
    col1,col2=st.columns(2)
    with col1:
        ec=d["event"].value_counts().reset_index()
        ec.columns=["Event","Count"]
        fig_e=px.bar(ec,x="Event",y="Count",color="Event",color_discrete_map=EVENT_COLORS)
        fig_e.update_layout(paper_bgcolor="#1a1a2e",plot_bgcolor="#1a1a2e",font=dict(color="white"),showlegend=False)
        st.plotly_chart(fig_e,use_container_width=True)
    with col2:
        dc=d.groupby("date")["event"].count().reset_index()
        dc.columns=["Date","Count"]
        fig_d=px.line(dc,x="Date",y="Count",markers=True)
        fig_d.update_layout(paper_bgcolor="#1a1a2e",plot_bgcolor="#1a1a2e",font=dict(color="white"))
        st.plotly_chart(fig_d,use_container_width=True)
