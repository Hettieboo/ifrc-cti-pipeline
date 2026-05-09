import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os

random.seed(42)
np.random.seed(42)

# --- CONFIG ---
COUNTRIES = [
    {"code": "KE", "name": "Kenya", "zone": "Africa", "emergency": False, "conflict": False},
    {"code": "NG", "name": "Nigeria", "zone": "Africa", "emergency": True, "conflict": True},
    {"code": "PH", "name": "Philippines", "zone": "Asia-Pacific", "emergency": True, "conflict": False},
    {"code": "CO", "name": "Colombia", "zone": "Americas", "emergency": False, "conflict": True},
    {"code": "UA", "name": "Ukraine", "zone": "Europe", "emergency": True, "conflict": True},
    {"code": "BD", "name": "Bangladesh", "zone": "Asia-Pacific", "emergency": True, "conflict": False},
    {"code": "ET", "name": "Ethiopia", "zone": "Africa", "emergency": True, "conflict": True},
    {"code": "MX", "name": "Mexico", "zone": "Americas", "emergency": False, "conflict": False},
]

REGIONS = {
    "KE": ["Nairobi", "Mombasa", "Kisumu", "Nakuru"],
    "NG": ["Lagos", "Kano", "Abuja", "Kaduna"],
    "PH": ["Metro Manila", "Cebu", "Davao", "Mindanao"],
    "CO": ["Bogota", "Medellin", "Cali", "Cartagena"],
    "UA": ["Kyiv", "Kharkiv", "Lviv", "Odessa"],
    "BD": ["Dhaka", "Chittagong", "Sylhet", "Cox's Bazar"],
    "ET": ["Addis Ababa", "Dire Dawa", "Tigray", "Amhara"],
    "MX": ["Mexico City", "Guadalajara", "Monterrey", "Oaxaca"],
}

AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
GENDERS = ["Female", "Male", "Non-binary", "Prefer not to say"]
DISPLACEMENT = ["Host community", "Displaced", "Refugee", "Returnee", "Not affected"]
COLLECTION_METHODS = ["KoboToolbox", "Paper", "Digital tablet", "Phone interview"]
TRUST_DIMENSIONS = ["competence", "integrity", "benevolence", "transparency"]

QUALITATIVE_THEMES = [
    "Staff behaviour", "Aid distribution", "Communication quality",
    "Community involvement", "Resource allocation", "Response speed",
    "Cultural sensitivity", "Transparency of operations", "Rumour/misinformation",
    "Access to services"
]

POSITIVE_RESPONSES = [
    "The Red Cross team was very helpful and respectful to our community",
    "We received food and medicine quickly after the flood",
    "Staff communicated clearly about what aid was available",
    "They listened to our needs and responded accordingly",
    "The volunteers were trained and professional",
    "Distribution was fair and transparent",
    "We trust them to help us in times of crisis",
    "They kept us informed throughout the process"
]

NEGATIVE_RESPONSES = [
    "We did not receive any information about the aid distribution",
    "Some families were excluded without explanation",
    "The response came too late after the emergency",
    "We heard the aid was being sold rather than distributed",
    "Communication was poor and we did not know who to contact",
    "There were rumours that staff were taking goods for themselves",
    "We felt our community was not prioritised compared to others",
    "The process was not transparent and we could not ask questions"
]

NEUTRAL_RESPONSES = [
    "We received some help but not everything we needed",
    "The team visited but we are not sure what happens next",
    "Some people got assistance but others did not",
    "We have heard mixed things about the organisation",
    "The response was okay but could have been faster",
    "We trust them somewhat but have had issues in the past"
]

os.makedirs("cti_data", exist_ok=True)

# --- GENERATE SURVEYS ---
surveys = []
survey_id = 1
start_date = datetime(2024, 1, 1)

for country in COUNTRIES:
    for quarter in range(1, 5):
        survey_date = start_date + timedelta(days=(quarter-1)*90 + random.randint(0, 30))
        surveys.append({
            "survey_id": f"S{survey_id:04d}",
            "survey_name": f"CTI {country['name']} Q{quarter} 2024",
            "survey_type": "mixed",
            "phase": "data_collection",
            "start_date": survey_date.strftime("%Y-%m-%d"),
            "end_date": (survey_date + timedelta(days=random.randint(14, 30))).strftime("%Y-%m-%d"),
            "country_code": country["code"],
            "national_society": f"{country['name']} Red Cross",
            "target_population": random.choice(DISPLACEMENT),
            "quarter": quarter,
            "year": 2024
        })
        survey_id += 1

surveys_df = pd.DataFrame(surveys)
surveys_df.to_csv("cti_data/dim_survey.csv", index=False)
print(f"Generated {len(surveys_df)} surveys")

# --- GENERATE GEOGRAPHY ---
geo_records = []
geo_id = 1
for country in COUNTRIES:
    for region in REGIONS[country["code"]]:
        geo_records.append({
            "geo_id": f"G{geo_id:04d}",
            "country_code": country["code"],
            "country_name": country["name"],
            "region": region,
            "district": f"{region} District",
            "ifrc_zone": country["zone"],
            "emergency_context": country["emergency"],
            "conflict_affected": country["conflict"]
        })
        geo_id += 1

geo_df = pd.DataFrame(geo_records)
geo_df.to_csv("cti_data/dim_geography.csv", index=False)
print(f"Generated {len(geo_df)} geography records")

# --- GENERATE TRUST DIMENSIONS ---
dimensions = []
dim_id = 1
questions = {
    "competence": [
        ("Q_C1", "The Red Cross/Red Crescent has the skills to help my community", "likert"),
        ("Q_C2", "They deliver what they promise", "likert"),
        ("Q_C3", "Their staff are well trained", "likert"),
    ],
    "integrity": [
        ("Q_I1", "The Red Cross/Red Crescent is honest in its dealings with my community", "likert"),
        ("Q_I2", "Aid is distributed fairly and without corruption", "likert"),
        ("Q_I3", "They follow through on commitments", "likert"),
    ],
    "benevolence": [
        ("Q_B1", "The Red Cross/Red Crescent genuinely cares about my community", "likert"),
        ("Q_B2", "They prioritise the most vulnerable people", "likert"),
        ("Q_B3", "They act in our best interests", "likert"),
    ],
    "transparency": [
        ("Q_T1", "The Red Cross/Red Crescent communicates clearly about what help is available", "likert"),
        ("Q_T2", "They explain how decisions are made", "likert"),
        ("Q_T3", "We can easily ask questions and get answers", "likert"),
    ]
}

for dimension, qs in questions.items():
    for q_code, q_text, q_type in qs:
        dimensions.append({
            "dimension_id": f"D{dim_id:03d}",
            "dimension_name": dimension,
            "question_code": q_code,
            "question_text": q_text,
            "question_type": q_type,
            "is_core_indicator": True
        })
        dim_id += 1

dim_df = pd.DataFrame(dimensions)
dim_df.to_csv("cti_data/dim_trust_dimension.csv", index=False)
print(f"Generated {len(dim_df)} trust dimension records")

# --- GENERATE SURVEY RESPONSES ---
responses = []
qualitative_responses = []
response_id = 1
qual_id = 1

for _, survey in surveys_df.iterrows():
    country = survey["country_code"]
    country_data = next(c for c in COUNTRIES if c["code"] == country)
    regions = REGIONS[country]
    n_responses = random.randint(80, 200)

    # Emergency contexts get lower trust scores
    base_trust = 2.8 if country_data["emergency"] and country_data["conflict"] else 3.5
    base_trust = base_trust + random.uniform(-0.3, 0.3)

    for _ in range(n_responses):
        region = random.choice(regions)
        geo = geo_df[(geo_df["country_code"] == country) & (geo_df["region"] == region)].iloc[0]

        resp = {
            "response_id": f"R{response_id:06d}",
            "survey_id": survey["survey_id"],
            "submission_date": survey["start_date"],
            "country_code": country,
            "geo_id": geo["geo_id"],
            "region": region,
            "collection_method": random.choice(COLLECTION_METHODS),
            "respondent_age_group": random.choice(AGE_GROUPS),
            "respondent_gender": random.choice(GENDERS),
            "respondent_displacement_status": random.choice(DISPLACEMENT),
            "language": "English",
            "ingested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_system": "KoboToolbox"
        }
        responses.append(resp)

        # Add qualitative response for 40% of respondents
        if random.random() < 0.4:
            sentiment_rand = random.random()
            if sentiment_rand < 0.4:
                text = random.choice(POSITIVE_RESPONSES)
                sentiment = round(random.uniform(0.3, 1.0), 3)
                sentiment_label = "positive"
                theme = random.choice(QUALITATIVE_THEMES[:5])
                rumour_flag = False
            elif sentiment_rand < 0.7:
                text = random.choice(NEGATIVE_RESPONSES)
                sentiment = round(random.uniform(-1.0, -0.2), 3)
                sentiment_label = "negative"
                theme = random.choice(QUALITATIVE_THEMES[5:])
                rumour_flag = "rumour" in text.lower() or "sold" in text.lower()
            else:
                text = random.choice(NEUTRAL_RESPONSES)
                sentiment = round(random.uniform(-0.2, 0.3), 3)
                sentiment_label = "neutral"
                theme = random.choice(QUALITATIVE_THEMES)
                rumour_flag = False

            qualitative_responses.append({
                "qualitative_id": f"Q{qual_id:06d}",
                "response_id": f"R{response_id:06d}",
                "survey_id": survey["survey_id"],
                "geo_id": geo["geo_id"],
                "submission_date": survey["start_date"],
                "free_text_response": text,
                "language": "English",
                "sentiment_score": sentiment,
                "sentiment_label": sentiment_label,
                "theme_code": theme.replace(" ", "_").upper(),
                "theme_label": theme,
                "nlp_confidence_score": round(random.uniform(0.75, 0.99), 3),
                "human_validated": random.choice([True, False]),
                "rumour_flag": rumour_flag,
                "ingested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            qual_id += 1

        response_id += 1

responses_df = pd.DataFrame(responses)
responses_df.to_csv("cti_data/survey_responses_bronze.csv", index=False)
print(f"Generated {len(responses_df)} survey responses")

qual_df = pd.DataFrame(qualitative_responses)
qual_df.to_csv("cti_data/qualitative_responses_bronze.csv", index=False)
print(f"Generated {len(qual_df)} qualitative responses")

# --- GENERATE FACT TRUST SCORES ---
fact_scores = []
score_id = 1

for _, response in responses_df.iterrows():
    country = response["country_code"]
    country_data = next(c for c in COUNTRIES if c["code"] == country)
    base = 2.8 if country_data["emergency"] and country_data["conflict"] else 3.5

    for _, dim in dim_df.iterrows():
        # Conflict countries score lower on integrity and transparency
        if country_data["conflict"] and dim["dimension_name"] in ["integrity", "transparency"]:
            score_base = base - 0.4
        else:
            score_base = base

        raw_score = round(min(5, max(1, np.random.normal(score_base, 0.8))), 0)
        normalised = round((raw_score - 1) / 4 * 100, 1)

        fact_scores.append({
            "score_id": f"SC{score_id:07d}",
            "response_id": response["response_id"],
            "survey_id": response["survey_id"],
            "geo_id": response["geo_id"],
            "dimension_id": dim["dimension_id"],
            "submission_date": response["submission_date"],
            "response_value": int(raw_score),
            "normalised_score": normalised,
            "weight_applied": 1.0,
            "is_validated": True
        })
        score_id += 1

fact_df = pd.DataFrame(fact_scores)
fact_df.to_csv("cti_data/fact_trust_scores_silver.csv", index=False)
print(f"Generated {len(fact_df)} trust score records")

# --- GENERATE GOLD MART ---
mart_records = []

for _, survey in surveys_df.iterrows():
    survey_scores = fact_df[fact_df["survey_id"] == survey["survey_id"]]
    if survey_scores.empty:
        continue

    geo_ids = survey_scores["geo_id"].unique()
    for geo_id_val in geo_ids:
        geo_scores = survey_scores[survey_scores["geo_id"] == geo_id_val]
        geo_info = geo_df[geo_df["geo_id"] == geo_id_val].iloc[0]

        overall = round(geo_scores["normalised_score"].mean(), 1)
        competence = round(geo_scores[geo_scores["dimension_id"].isin(
            dim_df[dim_df["dimension_name"] == "competence"]["dimension_id"])]["normalised_score"].mean(), 1)
        integrity = round(geo_scores[geo_scores["dimension_id"].isin(
            dim_df[dim_df["dimension_name"] == "integrity"]["dimension_id"])]["normalised_score"].mean(), 1)
        benevolence = round(geo_scores[geo_scores["dimension_id"].isin(
            dim_df[dim_df["dimension_name"] == "benevolence"]["dimension_id"])]["normalised_score"].mean(), 1)
        transparency = round(geo_scores[geo_scores["dimension_id"].isin(
            dim_df[dim_df["dimension_name"] == "transparency"]["dimension_id"])]["normalised_score"].mean(), 1)

        sample_size = len(geo_scores["response_id"].unique())
        alert_flag = overall < 45 or integrity < 40

        mart_records.append({
            "summary_id": f"M{len(mart_records)+1:05d}",
            "survey_id": survey["survey_id"],
            "geo_id": geo_id_val,
            "country_code": geo_info["country_code"],
            "country_name": geo_info["country_name"],
            "region": geo_info["region"],
            "ifrc_zone": geo_info["ifrc_zone"],
            "emergency_context": geo_info["emergency_context"],
            "conflict_affected": geo_info["conflict_affected"],
            "survey_date": survey["start_date"],
            "quarter": survey["quarter"],
            "year": survey["year"],
            "overall_trust_score": overall,
            "competence_score": competence,
            "integrity_score": integrity,
            "benevolence_score": benevolence,
            "transparency_score": transparency,
            "sample_size": sample_size,
            "alert_flag": alert_flag,
            "alert_reason": "Low trust score — review required" if alert_flag else ""
        })

mart_df = pd.DataFrame(mart_records)
mart_df.to_csv("cti_data/mart_trust_index_gold.csv", index=False)
print(f"Generated {len(mart_df)} gold mart records")

print("\n✅ All CTI datasets generated successfully in /cti_data/")
print("\nFiles created:")
for f in os.listdir("cti_data"):
    size = os.path.getsize(f"cti_data/{f}")
    print(f"  {f} ({size:,} bytes)")
