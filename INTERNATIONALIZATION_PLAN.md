# Internationalization & Location-Based Features Plan

## Executive Summary

> **Important Note on Current Multilingual Support:**
> The app currently uses Google Gemini AI which **can understand resumes and job descriptions in any language** (French, German, Spanish, etc.). However, all AI-generated feedback, recommendations, and analysis results are returned **in English only**. Phase 3 addresses this by adding language-aware prompts so responses match the user's preferred language.

This plan outlines how to make ResumeAnalyzer AI work globally, with location-based job matching, multi-language support, and multi-currency payments. The implementation is divided into 4 phases.

---

## Current State Analysis

### What Already Exists
- **User Model**: Has `preferred_location` field (string, not structured)
- **JobPosting Model**: Has `location`, `salary_currency` fields
- **Adzuna API**: Supports multiple country codes (us, gb, fr, de, etc.)
- **Market Intelligence**: Has `get_location_salary_insights()` method
- **Settings Page**: Has language/timezone UI fields (not persisted)

### What's Missing
- No i18n library or translation files
- Adzuna API hardcoded to "us" location
- All payments in USD only
- No country/region selection for users
- No location-based job filtering in matching algorithm

---

## Phase 1: User Location & Country Support

### 1.1 Database Schema Updates

**User Model Extensions:**
```python
# Add to backend/models.py - User class
country_code = db.Column(db.String(2), default='US', index=True)  # ISO 3166-1 alpha-2
language = db.Column(db.String(5), default='en')  # ISO 639-1 (en, fr, de, es)
timezone = db.Column(db.String(50), default='UTC')
preferred_currency = db.Column(db.String(3), default='USD')  # ISO 4217
```

**New Country Configuration Table:**
```python
class SupportedCountry(db.Model):
    __tablename__ = 'supported_countries'

    code = db.Column(db.String(2), primary_key=True)  # US, FR, GB, DE
    name = db.Column(db.String(100), nullable=False)
    native_name = db.Column(db.String(100))  # France, Deutschland
    default_language = db.Column(db.String(5), default='en')
    default_currency = db.Column(db.String(3), default='USD')
    adzuna_code = db.Column(db.String(5))  # Adzuna country code mapping
    is_active = db.Column(db.Boolean, default=True)
    job_board_available = db.Column(db.Boolean, default=True)
```

### 1.2 Supported Countries (Initial Launch)

| Country | Code | Currency | Adzuna Code | Language |
|---------|------|----------|-------------|----------|
| United States | US | USD | us | en |
| United Kingdom | GB | GBP | gb | en |
| Canada | CA | CAD | ca | en/fr |
| France | FR | EUR | fr | fr |
| Germany | DE | EUR | de | de |
| Australia | AU | AUD | au | en |
| Netherlands | NL | EUR | nl | nl/en |
| India | IN | INR | in | en |

### 1.3 Backend API Endpoints

**New Endpoints:**
```
GET  /api/config/countries          - List supported countries
GET  /api/config/languages          - List supported languages
GET  /api/config/currencies         - List supported currencies
POST /api/user/location             - Update user's country/location
GET  /api/user/location             - Get user's location settings
```

**Updated Endpoints:**
```
PUT  /api/user/preferences          - Add country_code, language, currency
GET  /api/user/profile              - Include location settings in response
```

### 1.4 Frontend Changes

**Settings Page Updates:**
- Add country selector dropdown
- Persist language/timezone/currency to backend
- Auto-detect country from browser on first visit

**New Location Context:**
```javascript
// frontend/src/context/LocationContext.jsx
const LocationContext = createContext({
  country: 'US',
  language: 'en',
  currency: 'USD',
  timezone: 'UTC'
});
```

---

## Phase 2: Location-Based Job Matching & Market Intelligence

### 2.1 Adzuna Service Updates

**File:** `backend/services/adzuna_service.py`

```python
# Current (hardcoded):
def fetch_jobs(self, industry, page=1):
    location = "us"
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/{page}"

# Updated (dynamic):
def fetch_jobs(self, industry, country_code='us', location_query=None, page=1):
    adzuna_country = self._map_country_code(country_code)
    url = f"https://api.adzuna.com/v1/api/jobs/{adzuna_country}/search/{page}"

    params = {
        'app_id': self.app_id,
        'app_key': self.api_key,
        'what': industry_keywords,
        'where': location_query,  # City/region within country
        'max_days_old': 30
    }
```

**Country Code Mapping:**
```python
ADZUNA_COUNTRY_MAP = {
    'US': 'us',
    'GB': 'gb',
    'CA': 'ca',
    'FR': 'fr',
    'DE': 'de',
    'AU': 'au',
    'NL': 'nl',
    'IN': 'in',
    'IT': 'it',
    'ES': 'es',
    'BR': 'br',
    'MX': 'mx',
    'PL': 'pl',
    'BE': 'be',
    'AT': 'at',
    'CH': 'ch',
    'NZ': 'nz',
    'SG': 'sg',
    'ZA': 'za'
}
```

### 2.2 Job Matcher Updates

**File:** `backend/services/job_matcher.py`

```python
def get_matches_for_user(self, user_id, limit=20):
    user = User.query.get(user_id)

    # Get user's country preference
    country_code = user.country_code or 'US'
    preferred_location = user.preferred_location  # City/region

    # Fetch jobs for user's country
    jobs = self.adzuna_service.fetch_jobs(
        industry=user.preferred_industry,
        country_code=country_code,
        location_query=preferred_location
    )

    # Filter and match with location weighting
    matches = self._calculate_matches(user, jobs, location_weight=0.15)
```

**Location-Aware Matching Score:**
```python
def _calculate_match_score(self, user, job):
    base_score = self._skill_match_score(user.skills, job.requirements)

    # Location bonus (if user prefers specific location)
    location_bonus = 0
    if user.preferred_location:
        if user.preferred_location.lower() in job.location.lower():
            location_bonus = 10
        elif job.remote_type == 'remote':
            location_bonus = 5

    return min(100, base_score + location_bonus)
```

### 2.3 Market Intelligence Location Filtering

**File:** `backend/routes_market_intelligence.py`

**Updated Endpoints:**
```python
@app.route('/api/market/skills/demand', methods=['GET'])
def get_skill_demand():
    country = request.args.get('country', 'US')
    location = request.args.get('location')  # Optional city/region

    # Filter market data by location
    demand_data = market_analyzer.get_skill_demand(
        country_code=country,
        location=location
    )
    return jsonify(demand_data)

@app.route('/api/market/salary-insights', methods=['GET'])
def get_salary_insights():
    country = request.args.get('country', 'US')
    skill = request.args.get('skill')
    location = request.args.get('location')

    insights = market_analyzer.get_location_salary_insights(
        country_code=country,
        location=location,
        skill_id=skill
    )
    return jsonify(insights)
```

### 2.4 Frontend Location Selector

**New Component:** `frontend/src/components/LocationSelector.jsx`
```javascript
const LocationSelector = ({ onLocationChange }) => {
  const [country, setCountry] = useState('US');
  const [city, setCity] = useState('');

  return (
    <div className="location-selector">
      <select value={country} onChange={handleCountryChange}>
        {SUPPORTED_COUNTRIES.map(c => (
          <option key={c.code} value={c.code}>{c.name}</option>
        ))}
      </select>
      <input
        placeholder="City or region (optional)"
        value={city}
        onChange={handleCityChange}
      />
    </div>
  );
};
```

**Integration Points:**
- Market Intelligence Dashboard header
- Job Matches filter bar
- User Settings page
- Onboarding flow

---

## Phase 3: Multi-Language Support (i18n)

### 3.0 AI Response Language (Critical for Non-English Users)

**Current Behavior:**
- Gemini AI understands French/German/Spanish resumes perfectly
- But all feedback, recommendations, cover letters are generated in English
- This creates a poor UX for non-English speakers

**Solution: Language-Aware AI Prompts**

**File:** `backend/gemini_service.py`

```python
class GeminiService:
    # Language instruction templates
    LANGUAGE_INSTRUCTIONS = {
        'en': 'Respond entirely in English.',
        'fr': 'Répondez entièrement en français. Utilisez un ton professionnel.',
        'de': 'Antworten Sie vollständig auf Deutsch. Verwenden Sie einen professionellen Ton.',
        'es': 'Responda completamente en español. Use un tono profesional.',
        'nl': 'Antwoord volledig in het Nederlands. Gebruik een professionele toon.',
        'pt': 'Responda inteiramente em português. Use um tom profissional.',
        'it': 'Rispondi interamente in italiano. Usa un tono professionale.'
    }

    def generate_personalized_feedback(self, resume_text: str, job_description: str,
                                       match_score: float, keywords_found: list,
                                       keywords_missing: list, language: str = 'en') -> str:
        """Generate feedback in the user's preferred language"""

        lang_instruction = self.LANGUAGE_INSTRUCTIONS.get(language, self.LANGUAGE_INSTRUCTIONS['en'])

        prompt = f"""You are an expert career coach and resume writer.
IMPORTANT: {lang_instruction}

Analyze this resume against the job description and provide specific, actionable feedback.

RESUME:
{resume_excerpt}

JOB DESCRIPTION:
{job_excerpt}
...
"""
```

**Auto-Detect Language from Resume:**

```python
def detect_document_language(self, text: str) -> str:
    """Detect the primary language of the resume/job description"""
    prompt = """Analyze this text and determine its primary language.
Return ONLY the ISO 639-1 two-letter code (en, fr, de, es, nl, pt, it).
If mixed languages, return the dominant one.

Text sample:
{text[:1000]}

Response (just the code):"""

    try:
        response = self._call_gemini_with_retry(prompt, "language_detection")
        detected = response.strip().lower()[:2]
        if detected in self.LANGUAGE_INSTRUCTIONS:
            return detected
        return 'en'
    except:
        return 'en'
```

**Integration in Analysis Endpoint:**

```python
# backend/app.py - analyze endpoint
@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    # ... existing code ...

    # Get user's language preference OR auto-detect from documents
    user_language = user.language if user else 'en'

    # Optionally auto-detect from resume if user hasn't set preference
    if user_language == 'en' and resume_text:
        detected_lang = gemini_service.detect_document_language(resume_text)
        if detected_lang != 'en':
            user_language = detected_lang

    # Generate feedback in detected/preferred language
    feedback = gemini_service.generate_personalized_feedback(
        resume_text, job_description, match_score,
        keywords_found, keywords_missing,
        language=user_language  # Pass language parameter
    )
```

**Functions to Update:**
1. `generate_personalized_feedback()` - Main analysis feedback
2. `generate_optimized_resume()` - Resume rewriting
3. `generate_cover_letter()` - Cover letter generation
4. `suggest_missing_experience()` - Skill suggestions
5. `extract_job_requirements()` - Job parsing (keep keywords in original language)
6. `extract_resume_content()` - Resume parsing
7. `generate_intelligent_recommendations()` - Career recommendations
8. `generate_ats_optimization_recommendations()` - ATS tips

**Keep Original Language for Keywords:**
```python
# When extracting keywords, keep them in original language
prompt = f"""Extract keywords from this job description.
Keep keywords in their ORIGINAL language (do not translate).
If the job is in French, return French keywords.
...
"""
```

### 3.1 Frontend i18n Setup

**Install Dependencies:**
```bash
cd frontend
npm install react-i18next i18next i18next-browser-languagedetector i18next-http-backend
```

**i18n Configuration:**
```javascript
// frontend/src/i18n/index.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: require('./locales/en.json') },
      fr: { translation: require('./locales/fr.json') },
      de: { translation: require('./locales/de.json') },
      es: { translation: require('./locales/es.json') },
    },
    fallbackLng: 'en',
    interpolation: { escapeValue: false }
  });

export default i18n;
```

### 3.2 Translation Files Structure

```
frontend/src/i18n/
├── index.js
└── locales/
    ├── en.json
    ├── fr.json
    ├── de.json
    ├── es.json
    └── nl.json
```

**Example Translation File (en.json):**
```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "loading": "Loading...",
    "error": "An error occurred"
  },
  "nav": {
    "dashboard": "Dashboard",
    "marketIntelligence": "Market Intelligence",
    "pricing": "Pricing",
    "settings": "Settings",
    "login": "Login",
    "signup": "Sign Up",
    "logout": "Logout"
  },
  "dashboard": {
    "welcome": "Welcome back, {{name}}!",
    "recentAnalyses": "Recent Analyses",
    "creditsRemaining": "{{count}} credits remaining",
    "analyzeResume": "Analyze Resume"
  },
  "market": {
    "jobMatches": "Job Matches",
    "interviewPrep": "Interview Prep",
    "companyIntel": "Company Intel",
    "careerPath": "Career Path",
    "skillGap": "Skill Gap Analysis",
    "matchScore": "{{score}}% Match"
  },
  "pricing": {
    "free": "Free",
    "pro": "Pro",
    "elite": "Elite",
    "perMonth": "/month",
    "mostPopular": "Most Popular",
    "getStarted": "Get Started",
    "currentPlan": "Current Plan"
  },
  "settings": {
    "profile": "Profile",
    "language": "Language",
    "country": "Country",
    "timezone": "Timezone",
    "currency": "Currency"
  }
}
```

**French Translation (fr.json):**
```json
{
  "common": {
    "save": "Enregistrer",
    "cancel": "Annuler",
    "loading": "Chargement...",
    "error": "Une erreur s'est produite"
  },
  "nav": {
    "dashboard": "Tableau de bord",
    "marketIntelligence": "Intelligence de marché",
    "pricing": "Tarifs",
    "settings": "Paramètres",
    "login": "Connexion",
    "signup": "S'inscrire",
    "logout": "Déconnexion"
  },
  "dashboard": {
    "welcome": "Bienvenue, {{name}} !",
    "recentAnalyses": "Analyses récentes",
    "creditsRemaining": "{{count}} crédits restants",
    "analyzeResume": "Analyser le CV"
  },
  "market": {
    "jobMatches": "Offres d'emploi",
    "interviewPrep": "Préparation d'entretien",
    "companyIntel": "Renseignements entreprise",
    "careerPath": "Parcours professionnel",
    "skillGap": "Analyse des compétences",
    "matchScore": "{{score}}% de correspondance"
  },
  "pricing": {
    "free": "Gratuit",
    "pro": "Pro",
    "elite": "Elite",
    "perMonth": "/mois",
    "mostPopular": "Le plus populaire",
    "getStarted": "Commencer",
    "currentPlan": "Forfait actuel"
  }
}
```

### 3.3 Component Integration

**Usage in Components:**
```javascript
import { useTranslation } from 'react-i18next';

const Dashboard = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('dashboard.welcome', { name: user.name })}</h1>
      <p>{t('dashboard.creditsRemaining', { count: user.credits })}</p>
      <button>{t('dashboard.analyzeResume')}</button>
    </div>
  );
};
```

### 3.4 Language Switcher Component

```javascript
// frontend/src/components/LanguageSwitcher.jsx
import { useTranslation } from 'react-i18next';

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'nl', name: 'Nederlands', flag: '🇳🇱' }
];

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (langCode) => {
    i18n.changeLanguage(langCode);
    // Also update user preference in backend
    updateUserPreference({ language: langCode });
  };

  return (
    <select value={i18n.language} onChange={(e) => changeLanguage(e.target.value)}>
      {LANGUAGES.map(lang => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  );
};
```

### 3.5 Backend Email Translations

**File:** `backend/email_templates/`

Create translated email templates:
```
backend/email_templates/
├── en/
│   ├── welcome.html
│   ├── verification.html
│   └── analysis_results.html
├── fr/
│   ├── welcome.html
│   ├── verification.html
│   └── analysis_results.html
└── de/
    └── ...
```

**Email Service Update:**
```python
def send_verification_email(self, recipient_email, recipient_name, verification_link, language='en'):
    template_path = f'email_templates/{language}/verification.html'
    subject = self.get_translated_subject('verification', language)
    # Load and render template
```

---

## Phase 4: Multi-Currency Payments

### 4.1 Currency Configuration

**Database Model:**
```python
class CurrencyConfig(db.Model):
    __tablename__ = 'currency_config'

    code = db.Column(db.String(3), primary_key=True)  # USD, EUR, GBP
    symbol = db.Column(db.String(5))  # $, €, £
    name = db.Column(db.String(50))
    decimal_places = db.Column(db.Integer, default=2)
    stripe_supported = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
```

**Pricing by Currency:**
```python
class TierPricing(db.Model):
    __tablename__ = 'tier_pricing'

    id = db.Column(db.Integer, primary_key=True)
    tier = db.Column(db.String(20))  # free, pro, elite
    currency = db.Column(db.String(3))
    price_cents = db.Column(db.Integer)  # Price in smallest currency unit
    stripe_price_id = db.Column(db.String(100))  # Stripe Price ID for this combo

    __table_args__ = (
        db.UniqueConstraint('tier', 'currency', name='unique_tier_currency'),
    )
```

### 4.2 Regional Pricing Table

| Tier | USD | EUR | GBP | CAD | AUD | INR |
|------|-----|-----|-----|-----|-----|-----|
| Pro | $9.99 | €8.99 | £7.99 | $12.99 | $14.99 | ₹799 |
| Elite | $49.99 | €44.99 | £39.99 | $64.99 | $74.99 | ₹3,999 |

### 4.3 Payment Flow Updates

**Backend (app.py):**
```python
@app.route('/api/payments/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    tier = request.args.get('tier')
    currency = request.args.get('currency', 'USD')

    # Get price for tier + currency combination
    pricing = TierPricing.query.filter_by(
        tier=tier,
        currency=currency
    ).first()

    if not pricing:
        return jsonify({'error': 'Currency not supported for this tier'}), 400

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': pricing.stripe_price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f"{FRONTEND_URL}/billing?success=true",
        cancel_url=f"{FRONTEND_URL}/pricing?canceled=true",
    )

    return jsonify({'sessionId': session.id})
```

### 4.4 Frontend Pricing Page Updates

```javascript
// PricingPageV2.jsx
const PricingPage = () => {
  const { currency } = useLocation();  // From LocationContext
  const [prices, setPrices] = useState({});

  useEffect(() => {
    // Fetch prices for user's currency
    fetchPrices(currency).then(setPrices);
  }, [currency]);

  const formatPrice = (amount) => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency
    }).format(amount / 100);
  };

  return (
    <div>
      <PricingTier
        name="Pro"
        price={formatPrice(prices.pro)}
        // ...
      />
    </div>
  );
};
```

### 4.5 Stripe Configuration

**Create Price IDs in Stripe Dashboard:**
- `price_pro_usd` - Pro tier in USD
- `price_pro_eur` - Pro tier in EUR
- `price_pro_gbp` - Pro tier in GBP
- `price_elite_usd` - Elite tier in USD
- `price_elite_eur` - Elite tier in EUR
- `price_elite_gbp` - Elite tier in GBP

**Environment Variables:**
```env
STRIPE_PRICE_PRO_USD=price_xxx
STRIPE_PRICE_PRO_EUR=price_xxx
STRIPE_PRICE_PRO_GBP=price_xxx
STRIPE_PRICE_ELITE_USD=price_xxx
STRIPE_PRICE_ELITE_EUR=price_xxx
STRIPE_PRICE_ELITE_GBP=price_xxx
```

---

## Implementation Roadmap

### Phase 1: User Location (Week 1-2)
1. Add database fields to User model
2. Create SupportedCountry table and seed data
3. Create location API endpoints
4. Update Settings page to persist location
5. Add country selector component

### Phase 2: Location-Based Jobs (Week 3-4)
1. Update Adzuna service for multi-country
2. Modify job matcher with location filtering
3. Update Market Intelligence endpoints
4. Add location filter UI to job matches
5. Test with multiple countries

### Phase 3: Multi-Language (Week 5-6)
1. Install and configure react-i18next
2. Create English translation file (extract all strings)
3. Create French and German translations
4. Update all components to use t() function
5. Add language switcher component
6. Translate email templates

### Phase 4: Multi-Currency (Week 7-8)
1. Create Stripe prices for each currency
2. Add currency database tables
3. Update payment endpoints
4. Update pricing page with currency selector
5. Test payments in different currencies
6. Add currency to billing page

---

## Testing Checklist

### Location Features
- [ ] User can select country in settings
- [ ] Country selection persists after logout
- [ ] Job matches reflect user's country
- [ ] Market stats show location-specific data
- [ ] Salary insights use correct currency for location

### Language Features
- [ ] Language auto-detects from browser
- [ ] User can change language in settings
- [ ] All UI strings translate correctly
- [ ] Date/number formats match locale
- [ ] Emails sent in user's language

### Currency Features
- [ ] Prices display in user's currency
- [ ] Stripe checkout uses correct currency
- [ ] Billing history shows correct currency
- [ ] Currency persists in user profile

---

## API Documentation

### New Endpoints Summary

```
# Location
GET  /api/config/countries
GET  /api/config/languages
GET  /api/config/currencies
POST /api/user/location
GET  /api/user/location

# Market Intelligence (updated)
GET  /api/market/skills/demand?country=FR&location=Paris
GET  /api/market/salary-insights?country=DE&skill=Python
GET  /api/job-matches?country=GB&location=London

# Payments (updated)
GET  /api/payments/pricing?currency=EUR
POST /api/payments/create-checkout-session?tier=pro&currency=EUR
```

---

## Environment Variables

```env
# Internationalization
SUPPORTED_COUNTRIES=US,GB,CA,FR,DE,AU,NL,IN
SUPPORTED_LANGUAGES=en,fr,de,es,nl
SUPPORTED_CURRENCIES=USD,EUR,GBP,CAD,AUD,INR
DEFAULT_COUNTRY=US
DEFAULT_LANGUAGE=en
DEFAULT_CURRENCY=USD

# Stripe Multi-Currency
STRIPE_PRICE_PRO_USD=price_xxx
STRIPE_PRICE_PRO_EUR=price_xxx
STRIPE_PRICE_PRO_GBP=price_xxx
STRIPE_PRICE_ELITE_USD=price_xxx
STRIPE_PRICE_ELITE_EUR=price_xxx
STRIPE_PRICE_ELITE_GBP=price_xxx

# Adzuna API (already exists)
ADZUNA_APP_ID=xxx
ADZUNA_API_KEY=xxx
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Adzuna API not available in some countries | Fall back to US jobs with remote filter |
| Translation quality issues | Use professional translation services |
| Currency conversion complexity | Use fixed regional pricing, not live conversion |
| Stripe not available in user's country | Show message and suggest alternative |
| Performance impact of i18n | Lazy load translation files |

---

## Success Metrics

- **User Adoption**: % of users selecting non-US country
- **Job Match Quality**: Match scores for international users
- **Payment Conversion**: Checkout completion rate by currency
- **Language Usage**: % of users using non-English language
- **Market Coverage**: Number of active job postings per country
