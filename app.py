from flask import Flask, render_template, request, redirect, send_file, abort
import os
import csv
import random

app = Flask(__name__)

# 📌 设置图片路径
BASE_DIR = "static/vc"
MNIST_DIR = os.path.join(BASE_DIR, "mnist")
CIFAR_DIR = os.path.join(BASE_DIR, "cifar")
RESULTS_FILE = "results.csv"

# 📌 确保 `results.csv` 存在
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Image"])  # 初始列头，仅包含 "Image"

# 📌 读取所有图片（原始 + 对抗）
def load_images(dataset_dir):
    original_path = os.path.join(dataset_dir, "original")
    if not os.path.exists(original_path):
        return []

    original = sorted(os.listdir(original_path))  # 获取 0-9 原始图片
    adversarial_methods = [d for d in os.listdir(dataset_dir) if d != "original"]

    images = []
    for label in original:
        adversarial_images = []
        for method in adversarial_methods:
            path = os.path.join(dataset_dir, method, label)
            if os.path.exists(path):
                adversarial_images.append((method, path))

        random.shuffle(adversarial_images)  # 🔀 打乱对抗样本顺序
        images.append({
            "original": os.path.join(dataset_dir, "original", label),
            "adversarial": adversarial_images
        })

    return images

# 📌 载入 MNIST 和 CIFAR 图片（限制前 10 组）
mnist_images = load_images(MNIST_DIR)[:10]
cifar_images = load_images(CIFAR_DIR)[:10]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form.to_dict(flat=False)  # 🔍 获取用户提交的数据
        print("🔥 Received Data:", data)  # ✅ 调试输出

        # ✅ 读取 `results.csv`，确保表头和已有数据
        file_exists = os.path.exists(RESULTS_FILE)

        if file_exists:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                reader = list(csv.reader(f))
        else:
            reader = []

        # ✅ 计算已有投票人数（当前列数 / 2，因为有 rank 和 score 两列）
        existing_voter_count = (len(reader[0]) - 1) // 2 if reader else 0
        new_vote_rank = f"Voter_{existing_voter_count + 1}_Rank"
        new_vote_score = f"Voter_{existing_voter_count + 1}_Score"

        # ✅ 处理数据，整理格式
        data_dict = {row[0]: row[1:] for row in reader}

        for key, values in data.items():
            if key.startswith("mnist_rank_") or key.startswith("cifar_rank_"):
                img_path = key.split("mnist_rank_")[-1].split("cifar_rank_")[-1]
            elif key.startswith("mnist_score_") or key.startswith("cifar_score_"):
                img_path = key.split("mnist_score_")[-1].split("cifar_score_")[-1]
            else:
                continue  # 忽略无关数据

            if img_path not in data_dict:
                data_dict[img_path] = [""] * (2 * existing_voter_count)  # 为空列填充

            if "rank" in key:
                data_dict[img_path].append(values[0])  # 存入 rank
                data_dict[img_path].append("")  # 预留 score 位置
            elif "score" in key:
                if len(data_dict[img_path]) == (2 * existing_voter_count + 1):
                    data_dict[img_path][-1] = values[0]  # 替换掉 "" 预留位置
                else:
                    data_dict[img_path].append("")  # 预留 rank 位置
                    data_dict[img_path].append(values[0])  # 存入 score

        # ✅ 生成 CSV 内容
        header = ["Image"] + [f"Voter_{i+1}_Rank" for i in range(existing_voter_count + 1)] + [f"Voter_{i+1}_Score" for i in range(existing_voter_count + 1)]
        new_data = [[img] + data_dict[img] for img in sorted(data_dict.keys())]

        # ✅ 重新写入 `results.csv`
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(new_data)

        print(f"✅ 投票结果已成功写入 {RESULTS_FILE}！")

        return redirect("/success")

    return render_template("index.html", mnist_images=mnist_images, cifar_images=cifar_images)

@app.route("/success")
def success():
    return """
    <h2>Submission Successful! Thank you for your participation.</h2>
    <a href='/'>Return</a>
    """

@app.route("/download")
def download_results():
    if not os.path.exists(RESULTS_FILE):
        return abort(404, description="Results file not found.")

    return send_file(RESULTS_FILE, as_attachment=True, mimetype="text/csv", download_name="results.csv")

if __name__ == "__main__":
    app.run(debug=True)
