import pandas as pd
import os

print("--- Pulse to Polyphony: Data Analysis ---")

# 1. Analyze Likert Scale Ratings
if os.path.exists("perceptual_study_results.csv"):
    df_ratings = pd.read_csv("perceptual_study_results.csv")
    
    print("\n[MEDIAN SCORES BY TRUE HEALTH STATE]")
    # Calculate median scores for non-parametric ordinal data
    medians = df_ratings.groupby("True_State")[["Clarity", "Stress_Urgency", "Reassurance", "Intuitive_Mapping"]].median()
    print(medians.to_markdown())
else:
    print("Ratings CSV not found. Ensure participants have submitted data.")

# 2. Analyze Grouping Accuracy
if os.path.exists("participant_groupings.csv"):
    df_groupings = pd.read_csv("participant_groupings.csv")
    print(f"\n[GROUPING DATA LOGGED FOR {len(df_groupings)} PARTICIPANTS]")
    print(df_groupings.head())
else:
    print("Grouping CSV not found.")