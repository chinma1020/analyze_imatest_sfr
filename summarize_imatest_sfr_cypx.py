# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np

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
    match = re.search(r"(\d+)%", str(location_str))
    return int(match.group(1)) if match else 100  # Default 100% (treated as Edge)

df["Distance_from_Center"] = df["Location"].apply(extract_percentage)

# **✅ Distance classification: Center / Edge**
df["Region"] = df["Distance_from_Center"].apply(lambda x: "Center" if x <= 30 else "Edge")

# **✅ Save DataFrame to Excel**
df.to_excel(debug1, index=False)

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re


# ==================================================

# %%
# ========== 1. 20-200mmレンズのみのグラフ ==========
df_20200 = df[df["lens"] == "Sigma20-200mm"].copy()
df_20200["lens_status"] = df_20200["lens"] + "_" + df_20200["focal_length_num"].astype(str) + "_F" + df_20200["fstop_num"].astype(str)
# plt.figure(figsize=(12, 6))
# sns.boxplot(data=df_20200, x="lens_status", y="MTF50", hue="Region", palette="Set2")
# plt.title("MTF50 Distribution: Sigma20-200mm Only", fontsize=14, fontweight='bold')
# plt.xlabel("Lens Status", fontsize=12)
# plt.ylabel("MTF50 (Resolution)", fontsize=12)
# plt.grid(axis="y", linestyle="--", alpha=0.7)
# plt.legend(title="Region")
# plt.show()

# ========== Sigma20-200mmのみのヒートマップ ==========
import seaborn as sns
# ピボットテーブルで焦点距離×F値のMTF50平均を作成
df_heatmap = df[df["lens"] == "Sigma20-200mm"].copy()
df_heatmap["MTF50"] = pd.to_numeric(df_heatmap["MTF50"], errors="coerce")
heatmap_data = df_heatmap.pivot_table(index="fstop_num", columns="focal_length_num", values="MTF50", aggfunc="mean")
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, fmt=".3f", cmap="viridis")
plt.title("MTF50 Heatmap: Sigma20-200mm", fontsize=14, fontweight='bold')
plt.xlabel("Focal Length (mm)")
plt.ylabel("F-stop")
plt.show()
# %%
# ========== 20-200mmの20mmのみのグラフ ==========
df_20200_20mm = df_20200[df_20200["focal_length_num"] == 20].copy()
import numpy as np

plt.figure(figsize=(8, 6))
sns.boxplot(data=df_20200_20mm, x=df_20200_20mm["fstop_num"].astype(str), y="MTF50", hue="Region", palette="Set2")
plt.title("MTF50 Distribution: Sigma20-200mm 20mm Only", fontsize=14, fontweight='bold')
plt.xlabel("F-stop", fontsize=12)
plt.ylabel("MTF50 (Resolution)", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.legend(title="Region")
plt.tick_params(axis="y", labelsize=10)

yticks = plt.gca().get_yticks()
yticks_desc = np.linspace(max(yticks), min(yticks), 10)
plt.yticks(yticks_desc)
plt.gca().invert_yaxis()

plt.show()


# %%
