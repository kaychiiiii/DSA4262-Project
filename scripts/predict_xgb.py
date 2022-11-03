import argparse
from xgboost import XGBClassifier
from utils import *

ap = argparse.ArgumentParser(description="This script will apply your model on new data and return the m6A predictions.")
ap.add_argument("-d", "--data", type=str, help="direct RNA-Seq data, processed by m6Anet (.json)", required=True)
ap.add_argument("-m", "--model", type=str, help="pre-trained model from training script", required=True)
ap.add_argument("-s", "--save_path", type=str, help="path to save predictions (.csv)", required=True)
args = ap.parse_args()

# Read in data json and convert it into a dataframe
df = get_data_dataframe(args.data)
df["str_transcript_position"] = df["transcript_position"].apply(str)

# Process the dataframe to generate new features
df, new_cols = process_data_dataframe(df)

# Selecting relevant features
Xte = df[["transcript_position", "0", "1", "2", "3", "4", "5", "6", "7", "8"] + list(new_cols)]

print("[INFO] Loading model...")
model = XGBClassifier()
model.load_model(args.model)

print("[INFO] Running inference...")
yhat_probs = model.predict_proba(Xte, iteration_range=(0, model.best_iteration + 1))
yhat = model.predict(Xte, iteration_range=(0, model.best_iteration + 1))
yhat1_probs = yhat_probs[:, 1]
df["score"] = yhat1_probs

print(f"[INFO] Saving predictions at {args.save_path}...")
df_res = df[["transcript_id", "str_transcript_position", "score"]]
df_res = df_res.rename(columns={"str_transcript_position": "transcript_position"})
df_res.to_csv(args.save_path, index=False)

print("[INFO] Done.")
