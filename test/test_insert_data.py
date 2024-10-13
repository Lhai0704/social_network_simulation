import json
import random
from typing import List, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.node import Node, Base  # 确保从包含 Node 类定义的文件中导入
from config import SQLALCHEMY_DATABASE_URL
from sqlalchemy.exc import IntegrityError


def generate_profile() -> Dict:
    names = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Jamie", "Riley", "Avery", "Quinn"]
    occupations = ["Teacher", "Engineer", "Artist", "Doctor", "Entrepreneur", "Student", "Chef", "Writer", "Scientist", "Athlete"]
    mbti_types = ["INTJ", "ENTJ", "INFJ", "ENFJ", "INTP", "ENTP", "INFP", "ENFP", "ISTJ", "ESTJ", "ISFJ", "ESFJ", "ISTP", "ESTP", "ISFP", "ESFP"]
    traits = ["Ambitious", "Creative", "Analytical", "Empathetic", "Confident", "Introverted", "Extroverted", "Organized", "Adaptable", "Curious"]
    interests = ["Technology", "Art", "Sports", "Travel", "Music", "Cooking", "Reading", "Gaming", "Fitness", "Nature"]
    social_platforms = ["Twitter", "Instagram", "LinkedIn", "TikTok", "Facebook", "Reddit", "YouTube"]
    content_types = ["Photos", "Short videos", "Long-form posts", "Memes", "Professional updates", "Personal stories"]
    communication_tones = ["Formal", "Casual", "Humorous", "Serious", "Enthusiastic", "Reserved"]
    education_levels = ["High School", "Bachelor's Degree", "Master's Degree", "PhD", "Self-taught"]
    life_experiences = ["Lived abroad", "Started a business", "Changed careers", "Overcame a major challenge", "Learned a new skill", "Volunteered extensively"]

    return {
        "basic_info": {
            "name": random.choice(names),
            "age": random.randint(18, 65),
            "gender": random.choice(["Male", "Female", "Non-binary"]),
            "location": f"{random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])}, USA",
            "occupation": random.choice(occupations)
        },
        "personality": {
            "mbti_type": random.choice(mbti_types),
            "traits": random.sample(traits, 3),
            "interests": random.sample(interests, 3)
        },
        "social_media": {
            "favorite_platforms": random.sample(social_platforms, 2),
            "posting_frequency": random.choice(["Daily", "Weekly", "Monthly", "Rarely"]),
            "typical_content": random.sample(content_types, 2)
        },
        "communication_style": {
            "tone": random.choice(communication_tones),
            "formality_level": random.choice(["Very formal", "Somewhat formal", "Neutral", "Casual", "Very casual"]),
            "preferred_topics": random.sample(interests, 2)
        },
        "background": {
            "education": random.choice(education_levels),
            "life_experiences": random.sample(life_experiences, 2)
        }
    }


def insert_profiles_to_db(profiles: List[Dict], db_url: str):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for profile in profiles:
        base_name = profile['basic_info']['name']
        suffix = 0
        while True:
            try:
                name = f"{base_name}{suffix if suffix else ''}"
                new_node = Node(
                    name=name,
                    profile=profile
                )
                session.add(new_node)
                session.commit()
                break  # 如果成功插入，跳出循环
            except IntegrityError:
                session.rollback()  # 回滚事务
                suffix += 1  # 增加后缀
                profile['basic_info']['name'] = name  # 更新 profile 中的名字

    session.close()


# 生成 10 个配置文件
profiles = [generate_profile() for _ in range(10)]

# 数据库连接 URL
# db_url = 'mysql+mysqlconnector://your_username:your_password@localhost/your_database_name'

# 将配置文件插入数据库
insert_profiles_to_db(profiles, SQLALCHEMY_DATABASE_URL)

print("10 个用户配置文件已生成并插入数据库。")
