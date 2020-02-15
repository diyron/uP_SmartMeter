

# 9 folgenden Bytes ist die Server ID
# Gerätenummer (9 Bytes) nach dieser Sequenz
obis_srvid_a = "0177070100000009ff010101010b09"   # 1-0:0.0.9   -- variante A

# Energiemengen-Register (kWh)
obis_180 = "0177070100010800ff"     # 1-0:1.8.0

# Wirkleistung (W)
obis_1670 = "0177070100100700FF"    # 1-0:16.7.0 Gesamtleistung in [W]
obis_3670 = "0177070100240700FF"    # 1-0:36.7.0 Leistung L1
obis_5670 = "0177070100380700FF"    # 1-0:56.7.0 Leistung L2
obis_7670 = "01770701004C0700FF"    # 1-0:76.7.0 Leistung L3

obis_pubkey = "77078181C78205FF"    # Public Key des Zählers

ident_sc_unit_kWh = "621e52"  # -- ab dem 3. folgenden Byte lesen
ident_sc_unit_W = "621b52"


# not used
# obis_5470 = "0177070100380700FF"     #-- 1-0:54.7.0
# obis_9690201 = "0177070100605A0201"  # -- 1-0:96.90.2*01
# obis_9797000 = "017707010061610000"  # -- 1-0:97.97.0*00
# obis_200 = "0177070100000200000"     #-- 1-0:0.2.0*00    -- Firmware
# obis_181 = "0177070100010801FF"     # 1-0:1.8.1
# obis_182 = "0177070100010802FF"     # 1-0:1.8.2
# obis_280 = "0177070100020800FF"     # 1-0:2.8.0
# obis_281 = "0177070100020801FF"     # 1-0:2.8.1
# obis_282 = "0177070100020802FF"     # 1-0:2.8.2
# obis_srvid_b = "0177070100600100FF010101010B0A"   # 1-0:96.1.0  -- variante B


def extract_sml(rawsml: str):

    # device id =================================================
    # 01 455359 11 03A949EB
    n = rawsml.find(obis_srvid_a)
    #print("devid at", n)
    n = n + len(obis_srvid_a)
    devid = rawsml[n + 1]
    vendor_raw = rawsml[n + 2:n + 8] # ESY# 1s
    devid = devid + " " + vendor_raw
    devid = devid + " " + rawsml[n + 8:n + 10]  # 11
    devid = devid + " " + str(int(rawsml[n + 11:n + 18], 16))

    print("devid", devid)


    # count A+ 1.8.0 ===========================================
    n = rawsml.find(obis_180)
    #print("obis 180 at", n)
    n = n + len(obis_180)
    n = rawsml.find(ident_sc_unit_kWh, n, n+20)  # starts searching starting from n
    #print("ident at", n)
    n = n + len(ident_sc_unit_kWh)
    # das 1. folgende Byte enthalt den scaler
    #print("scaler at", n)
    #print("scaler raw", rawsml[n:n+2])
    scaler = int(rawsml[n:n+2], 16) - 256  # 10^scaler
    #print("scaler", scaler)
    # die Hälfte des 2. Byte (0x59 --> 9 --> 9 - 1 = 8 Byte) enthält die Byteanzahl
    vallen = int(rawsml[n+3], 16) - 1
    #print("vallen", vallen)
    val_kwh = rawsml[n+4:n+4+(vallen*2)]
    #print("value raw", val_kwh)
    value = int(val_kwh, 16)
    #print("value", value)
    value_num = value * (10 ** scaler)
    #print("value_num", value_num)
    value_h = value // (10 ** (scaler * -1))
    #print("value_h", value_h)
    value_l = value % (10 ** (scaler * -1))
    #print("value_l", value_l)

    meter_data = {
        "devid": devid,
        "1.8.0_Wh": (str(value_h) + "." + str(value_l))
    }

    #print("1.8.0 (Wh)", meter_data["1.8.0_Wh"])

    return meter_data


    # meter_data["16.7.0_W"] = rawsml[tmp:tmp + 9]
    # meter_data["36.7.0_W"] = rawsml[tmp:tmp + 9]
    # meter_data["56.7.0_W"] = rawsml[tmp:tmp + 9]
    # meter_data["76.7.0_W"] = rawsml[tmp:tmp + 9]


