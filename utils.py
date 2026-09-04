import os, json, logging, hashlib
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_dirs():
    for d in ['data', 'data/uploads', 'static/css', 'static/js', 'templates']:
        os.makedirs(d, exist_ok=True)

def get_db_path():
    return os.path.join('data', 'quiz.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_questions():
    path = os.path.join('data', 'questions.json')
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load questions: {e}")
        return []

def save_questions(questions):
    path = os.path.join('data', 'questions.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def get_topic_keywords():
    return {
        'Alcohol': ['alcohol', 'hydroxyl', '–OH', 'primary', 'secondary', 'tertiary', 'dehydration', 'oxidation', 'Lucas', 'KMnO4', 'Jones', 'phenol', 'ethanol', 'methanol'],
        'Chemical Kinetics': ['rate', 'kinetics', 'order', 'half-life', 'activation', 'Arrhenius', 'collision', 'catalyst', 'rate constant', 'elementary', 'mechanism'],
        'Electrochemistry': ['electrode', 'potential', 'cell', 'Nernst', 'faraday', 'electrolysis', 'oxidation', 'reduction', 'cathode', 'anode', 'E°', 'Gibbs'],
        'Ether': ['ether', '–O–', 'diethyl', 'epoxide', 'THF', 'peroxide', 'clearance', 'Williamson', 'SN2', 'sulfuric'],
        'Haloalkanes': ['halide', 'alkyl halide', 'chloro', 'bromo', 'iodo', 'fluoro', 'SN1', 'SN2', 'E1', 'E2', 'Zaitsev', 'Markovnikov'],
        'HaloArenes': ['aryl halide', 'aryl', 'nucleophilic', 'benzyne', 'aryne', 'halogen', 'directing', 'ortho', 'para', 'meta', 'SNAr'],
        'Nuclear Chemistry': ['nuclear', 'radioactive', 'decay', 'alpha', 'beta', 'gamma', 'fission', 'fusion', 'isotope', 'half-life', 'radiocarbon', 'curie', 'becquerel'],
        'Phenol': ['phenol', '–OH', 'aromatic', 'electrophilic', 'bromine', 'FeCl3', 'acidic', 'pKa', 'nitration', 'sulphonation', 'Friedel'],
        'Transition Metal': ['transition', 'd-block', 'oxidation', 'coordination', 'crystal', 'ligand', 'colour', 'paramagnetic', 'crystal field', 'd-d']
    }

def get_all_topics():
    return ['Alcohol', 'Chemical Kinetics', 'Electrochemistry', 'Ether', 'Haloalkanes', 'HaloArenes', 'Nuclear Chemistry', 'Phenol', 'Transition Metal']

def topic_for_question(question_text, correct_answer):
    keywords = get_topic_keywords()
    combined = (question_text + ' ' + correct_answer).lower()
    best_topic = 'General'
    best_count = 0
    for topic, kws in keywords.items():
        count = sum(1 for kw in kws if kw.lower() in combined)
        if count > best_count:
            best_count = count
            best_topic = topic
    return best_topic if best_count > 0 else 'General'
