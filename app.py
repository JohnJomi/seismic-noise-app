import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from obspy.clients.fdsn import Client
from obspy import UTCDateTime, Trace, Stream

st.title("🌍 Seismic Noise Removal App (ObsPy + Streamlit)")

# User inputs
network = st.text_input("Network Code", "XB")
station = st.text_input("Station Code", "ELYSE")
location = st.text_input("Location Code", "02")
channel = st.text_input("Channel (use ? for wildcard)", "BH?")
start_str = st.text_input("Start Time (UTC)", "2021-09-18T18:24:00")
end_str = st.text_input("End Time (UTC)", "2021-09-18T18:28:00")

if st.button("Fetch & Process Data"):
    try:
        client = Client("IRIS")
        start = UTCDateTime(start_str)
        end = UTCDateTime(end_str)

        # Fetch waveforms
        st_raw = client.get_waveforms(network, station, location, channel, start, end)
        st_raw.merge(method=1, fill_value="interpolate")
        st_raw.sort()
        st.write("✅ Data fetched:", st_raw)

        assert len(st_raw) == 3, f"Expected 3 traces, got {len(st_raw)}"

        # Preprocess
        st_proc = st_raw.copy()
        st_proc.detrend("demean")
        st_proc.detrend("linear")
        st_proc.taper(max_percentage=0.05, type="cosine")

        # Bandpass filter
        st_band = st_proc.copy()
        st_band.filter("bandpass", freqmin=0.1, freqmax=1.0, corners=4, zerophase=True)

        # Polarization filter
        data = np.vstack([tr.data for tr in st_band]).T
        C = np.cov(data.T)
        eigvals, eigvecs = np.linalg.eigh(C)
        idx = np.argsort(eigvals)[::-1]
        v1 = eigvecs[:, idx[0]]
        proj = data @ v1

        tr_pol = Trace(data=proj.astype(np.float32), header=st_band[0].stats)
        st_pol = Stream([tr_pol])

        # Plot Raw vs Polarized
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        for tr in st_raw:
            ax[0].plot(tr.times(), tr.data, label=tr.stats.channel)
        ax[0].set_title("Raw Data")
        ax[0].legend()

        ax[1].plot(st_pol[0].times(), st_pol[0].data, color="green")
        ax[1].set_title("Polarized (Cleaned) Data")
        st.pyplot(fig)

        # Download cleaned data
        csv_data = "\n".join(map(str, st_pol[0].data))
        st.download_button("Download Cleaned CSV", csv_data, "seismic_data_final.csv")

    except Exception as e:
        st.error(f"❌ Error: {e}")