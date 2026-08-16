import os
from dotenv import load_dotenv

load_dotenv()

# ================ TELEGRAM ================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', '0'))

# ================ API KEYS (HYBRID MODELS) ================
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '')

# ================ GITHUB ================
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# ================ DATABASE ================
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///digital_castle.db')

# ================ SERVER CONFIG ================
PORT = int(os.getenv('PORT', '8080'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:8080')

# ================ MODEL ASSIGNMENTS (HYBRID ROUTING) ================
MODELS = {
    'planning': {
        'provider': 'anthropic',
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 4000,
        'description': 'التخطيط والجدوى والمواصفات والتحليل'
    },
    'development': {
        'provider': 'deepseek',
        'model': 'deepseek-coder',
        'max_tokens': 6000,
        'description': 'كتابة الكود والبرمجة والأمان والـ Migrations'
    },
    'fast_tasks': {
        'provider': 'together',
        'model': 'meta-llama/Llama-3-70b-chat-hf',
        'max_tokens': 2000,
        'description': 'المهام السريعة والجودة والمحتوى والمراقبة'
    }
}

# ================ COMPANY IDENTITY ================
COMPANY_NAME = 'Digital Castle S.P.C'
COMPANY_AR_NAME = 'شركة القلعة الرقمية ش.ش.و'
COMPANY_REGISTRY = 'شركة متوقفة الترخيص'
BRAND_COLORS = {
    'primary': '#1a1a1a',
    'secondary': '#5B21B6',
    'accent': '#F59E0B',
    'success': '#10B981',
    'danger': '#EF4444'
}

# ================ PROJECT STRUCTURE ================
PROJECT_DIRS = {
    'assets': 'assets/',
    'brand_kit': 'brand-kit/',
    'specs': '.spec-kit/',
    'docs': 'docs/',
    'agents': 'agents/',
    'templates': 'brand-kit/templates/',
    'logs': 'logs/'
}

# ================ TOKEN LIMITS (COST OPTIMIZATION) ================
TOKEN_LIMITS = {
    'anthropic_monthly': 500000,
    'deepseek_monthly': 300000,
    'together_monthly': 200000,
    'warning_threshold': 0.8  # تنبيه عند استهلاك 80%
}

# ================ SECURITY ================
ALLOWED_ADMIN_IDS = [TELEGRAM_ADMIN_ID]
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-secret-key-change-in-production')

# ================ LOGGING ================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'logs/digital_castle.log'
