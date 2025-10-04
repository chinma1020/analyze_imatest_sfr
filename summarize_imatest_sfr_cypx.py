# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# **✅ ファイルのパス（変更しない）**
base_path = "C:/Users/chinm/Videos/PremierePro/20250925_sigma20-200/解像度/画像切り出し/imatest_input/Results"
file_path = f"{base_path}/SFR_cypx.csv"
debug1 = f"{base_path}/check_filtered.xlsx"

# **✅ ファイルを読み込む**
df = pd.read_csv(file_path, header=0, keep_default_na=False)

# **✅ カラム名のクリーンアップ**
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace("/n", "", regex=True)
df.columns = df.columns.str.replace(" ", "_", regex=True)

# **✅ "File" カラムの特定**
file_column = next((col for col in df.columns if "File" in col), None)
if file_column is None:
    raise ValueError("⚠️ 'File' column not found. Please check the CSV header.")

# **✅ 必要なカラムを選択**
columns_to_keep = ["H/V", "MTF50_C/P", "Chr_Aber_area_pxls", "Edge_Angle", "Location"]
existing_columns = [col for col in columns_to_keep if col in df.columns]

# **✅ データフレームを更新**
df = df[[file_column] + existing_columns]

# **✅ カラム名のリネーム**
df.rename(columns={"MTF50_C/P": "MTF50", "MTF30": "MTF30"}, inplace=True)

# **✅ "File" カラムを分割**
df[["lens", "focal_length", "fstop"]] = df[file_column].str.replace(".tif", "", regex=False).str.split("_", expand=True)
# **✅ fstopから'.MOV'以降を分離し、数値部分と動画情報に分割**
fstop_split = df["fstop"].str.split(".MOV", n=1, expand=True)
df["fstop"] = fstop_split[0]
df["mov_info"] = fstop_split[1] if fstop_split.shape[1] > 1 else None

    # **✅ focal_length を数値化（例: '020'→20, '200'→200）**
df["focal_length_num"] = df["focal_length"].astype(int)

# **✅ F-stop を小数点第一位の値に変換（例: '40'→4.0, '120'→12.0）**
df["fstop_num"] = pd.to_numeric(df["fstop"], errors="coerce") / 10


# **✅ 元の "File" カラムは削除**
# df.drop(columns=[file_column], inplace=True)

# %%

# **✅ "MedTeleMode" カラムの値を分かりやすくする**
df["lens"] = df["lens"].map({
    "l1": "Sigma20-200mm",
    "l2": "Lumix S24-105mm",
    "l3": "Lumix S70-300mm",
    "l4": "Sigma150-600mm"
}).fillna(df["lens"])



# **✅ Location の値から距離情報を抽出**
def extract_percentage(location_str):
    match = re.search(r"(/d+)%", str(location_str))
    return int(match.group(1)) if match else 100  # Default 100% (treated as Edge)

df["Distance_from_Center"] = df["Location"].apply(extract_percentage)

# **✅ Distance classification: Center / Edge**
df["Region"] = df["Distance_from_Center"].apply(lambda x: "Center" if x <= 30 else "Edge")

# **✅ Save DataFrame to Excel**
df.to_excel(debug1, index=False)

# %%
# **✅ Display DataFrame**
print(df)
# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# ここからグラフ作成
# ==============================================
# **✅ ズームモードの分類**
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# # **✅ ズームモードの分類**
# df["Zoom_Type"] = df.apply(lambda row: 
#     "No Zoom" if row["MedTeleMode"] == "Med-Tele Mode OFF" and row["DigitalZoom"] == "Digital Zoom OFF" and row["UlanziLens"] == "Ulanzi Lens OFF" else
#     "Med-Tele Mode" if row["MedTeleMode"] == "Med-Tele Mode 2x" and row["UlanziLens"] == "Ulanzi Lens OFF" and row["DigitalZoom"] == "Digital Zoom OFF" else
#     "Ulanzi Lens" if row["UlanziLens"] == "Ulanzi Lens ON" and row["MedTeleMode"] == "Med-Tele Mode OFF" and row["DigitalZoom"] == "Digital Zoom OFF" else
#     "Digital Zoom" if row["DigitalZoom"] == "Digital Zoom ON" and row["MedTeleMode"] == "Med-Tele Mode OFF" and row["UlanziLens"] == "Ulanzi Lens OFF" else "Other", axis=1)

# # **"Other" の行を除外**
# df = df[df["Zoom_Type"] != "Other"]

# # **✅ 視認性を向上した箱ひげ図**
# plt.figure(figsize=(12, 6))
# sns.boxplot(data=df, x="Zoom_Type", y="MTF50", hue="Region", palette="Set2")

# # **✅ タイトルや軸ラベルを強調**
# plt.title("MTF50 Distribution: No Zoom vs Med-Tele Mode vs Ulanzi Lens vs Digital Zoom", fontsize=14, fontweight='bold')
# plt.xlabel("Zoom Type", fontsize=12)
# plt.ylabel("MTF50 (Resolution)", fontsize=12)

# # **✅ 補助線を追加（Y軸）**
# plt.grid(axis="y", linestyle="--", alpha=0.7)

# # **✅ 凡例の設定**
# plt.legend(title="Region")

# # **✅ グラフの表示**
# plt.show()


# ==================================
# **✅ 複数条件（組み合わせ）のズームモード分類**
df["Zoom_Type"] = df.apply(lambda row: 
    "Med-Tele + Ulanzi" if row["MedTeleMode"] == "Med-Tele Mode 2x" and row["UlanziLens"] == "Ulanzi Lens ON" and row["DigitalZoom"] == "Digital Zoom OFF" else
    "Med-Tele + Digital Zoom" if row["MedTeleMode"] == "Med-Tele Mode 2x" and row["DigitalZoom"] == "Digital Zoom ON" and row["UlanziLens"] == "Ulanzi Lens OFF" else
    "Ulanzi + Digital Zoom" if row["UlanziLens"] == "Ulanzi Lens ON" and row["DigitalZoom"] == "Digital Zoom ON" and row["MedTeleMode"] == "Med-Tele Mode OFF" else
    "Med-Tele + Ulanzi + Digital Zoom" if row["MedTeleMode"] == "Med-Tele Mode 2x" and row["UlanziLens"] == "Ulanzi Lens ON" and row["DigitalZoom"] == "Digital Zoom ON" else "Other", axis=1)

# **"Other" の行を除外（単独条件のみのデータを除外）**
df = df[df["Zoom_Type"] != "Other"]

# **✅ 視認性を向上した箱ひげ図（複数条件のみ）**
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x="Zoom_Type", y="MTF50", hue="Region", palette="Set2")

# **✅ タイトルや軸ラベルを強調**
plt.title("MTF50 Distribution: Combined Zoom Modes (Med-Tele + Ulanzi, etc.)", fontsize=14, fontweight='bold')
plt.xlabel("Zoom Type", fontsize=12)
plt.ylabel("MTF50 (Resolution)", fontsize=12)

# **✅ 補助線を追加（Y軸）**
plt.grid(axis="y", linestyle="--", alpha=0.7)

# **✅ 凡例の設定**
plt.legend(title="Region")

# **✅ グラフの表示**
plt.show()

# ==================================================

# %%
