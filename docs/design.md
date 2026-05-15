# Vocab in News - Design Document

## Project Overview

**Vocab in News** is a personalized English vocabulary learning application that integrates real-world news articles with adaptive learning algorithms. The app helps users learn vocabulary in context through daily news content, enhanced with AI-powered word substitution and text-to-speech functionality.

## Core Concept

Instead of traditional flashcard-based learning, users acquire vocabulary through contextual reading of current news articles where target vocabulary words are strategically integrated without altering the article's meaning.

## Key Features

### 1. Personalized Learning Paths
- Support for multiple proficiency levels (TOEFL, GRE, SAT, General English)
- Customizable vocabulary lists based on user goals
- Adaptive difficulty progression
- Progress tracking and analytics

### 2. Context-Based Learning
- Daily generation of short news articles (200-400 words)
- AI-powered vocabulary integration maintaining semantic accuracy
- Real-world relevance through current events
- Natural language exposure

### 3. Spaced Repetition System
- Scientifically-backed memory retention algorithm
- Personalized review schedules
- Performance-based word prioritization
- Long-term retention optimization

### 4. Audio Learning
- Text-to-speech (TTS) integration for pronunciation
- Multiple voice options and speed controls
- Audio-first learning mode support
- Accessibility compliance

## System Architecture

### High-Level Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend App  │    │  Backend API    │    │  External APIs  │
│                 │    │                 │    │                 │
│ - User Interface│◄──►│ - User Mgmt     │◄──►│ - News APIs     │
│ - Audio Player  │    │ - Learning Logic│    │ - AI/LLM APIs   │
│ - Progress UI   │    │ - Content Mgmt  │    │ - TTS Services  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    Database     │
                    │                 │
                    │ - User Profiles │
                    │ - Vocab Lists   │
                    │ - Learning Data │
                    │ - Content Cache │
                    └─────────────────┘
```

### Core Services

#### 1. User Management Service (TODO: P2)
- User registration and authentication
- Profile management and preferences
- Learning goal configuration
- Progress tracking and analytics

#### 2. Vocabulary Management Service
- Curated vocabulary databases (TOEFL, GRE, etc.)
- Difficulty level classification (TODO: we need some stemmer technique to identify the difficulty for each word)
- Word metadata (definitions, pronunciations, examples)
- User-specific vocabulary tracking

#### 3. Content Generation Service
- News article fetching and filtering (TODO: for now we can manually feed)
- AI-powered vocabulary integration
- **Hybrid content creation**: News-based + AI-generated articles
- **Fallback article generation**: For words that cannot be naturally substituted
- Content quality validation
- Daily content scheduling

#### 4. Learning Algorithm Service
- Spaced repetition calculation
- Performance analysis
- Adaptive difficulty adjustment
- Review scheduling optimization

#### 5. Audio Service (TODO: P2, can be done later)
- TTS integration and management
- Audio file caching
- Playback speed controls
- Voice selection options

## Detailed Feature Specifications

### Personalized Learning Paths

#### Supported Vocabulary Lists
- **TOEFL**: ~3,000 academic vocabulary words
- **GRE**: ~4,000 graduate-level words  
- **SAT**: ~2,500 college-prep vocabulary
- **General English**: ~5,000 common advanced words
- **Custom Lists**: User-defined vocabulary sets

#### User Onboarding Flow
1. Skill assessment quiz (20-30 questions)
2. Learning goal selection
3. Daily time commitment preference
4. Difficulty preference configuration
5. Initial vocabulary list generation

#### Progress Tracking
- Words learned vs. total vocabulary
- Daily/weekly/monthly progress charts
- Retention rate analytics
- Time spent learning metrics
- Streak tracking and achievements

### Content Generation Pipeline

#### News Article Processing
1. **Source Selection**: Curated news sources (Reuters, AP, BBC, etc.)
2. **Content Filtering**: 
   - Article length: 200-400 words
   - Reading level: Appropriate for target audience
   - Topic diversity: World news, technology, science, culture
   - **Content Safety**: Filter out overly political, harmful, or inappropriate content for teenage users
3. **Difficulty Pre-Processing**:
   - Identify complex words in source articles (e.g., BBC content has inherently high vocabulary level)
   - Match against target vocabulary lists using stemming for accurate comparison
   - Flag words that may be challenging for user's current level
4. **Quality Control**: Grammar and coherence validation

#### AI-Powered Vocabulary Integration
1. **Word Selection Algorithm**:
   - Choose 8-12 target words per article
   - Balance new words (70%) vs. review words (30%)
   - Consider spaced repetition schedule
   - Maintain contextual appropriateness
   - **Stemming-Based Matching**: Use word stemming before comparing against user's vocabulary lists
   - Prioritize words from user's target learning list (TOEFL, GRE, etc.)

2. **Semantic Substitution Process**:
   - Identify replaceable words/phrases in original text
   - Generate contextually appropriate substitutions
   - Preserve article meaning and readability
   - Validate grammatical correctness
   - **Word Highlighting**: Mark substituted words for UI highlighting
   - **Substitution Feasibility Check**: Determine if target words can be naturally integrated

3. **Quality Assurance**:
   - Semantic similarity validation
   - Readability score maintenance
   - Manual review for edge cases

#### Example Transformation
**Original**: "The company announced significant changes to their policy."
**Enhanced**: "The corporation proclaimed substantial modifications to their protocol."
- Target words: corporation, proclaimed, substantial, modifications, protocol

### Spaced Repetition Algorithm

#### Core Algorithm: SM-2 Enhanced
- Initial interval: 1 day
- Subsequent intervals based on performance
- Difficulty factor adjustment (1.3 - 2.5)
- Performance threshold: 60% for progression

#### Review Scheduling
- **New words**: Introduced in daily articles
- **Review words**: Scheduled based on forgetting curve
- **Difficult words**: Increased frequency until mastery
- **Mastered words**: Long-term maintenance schedule

#### Performance Metrics
- **Comprehension**: Multiple choice questions
- **Context usage**: Fill-in-the-blank exercises
- **Recognition speed**: Timed identification
- **Retention rate**: Long-term memory assessment

### Audio Integration

#### TTS Implementation
- **Primary**: Cloud-based TTS (Google Cloud, AWS Polly)
- **Fallback**: Local TTS for offline usage
- **Voice Options**: Multiple accents and genders
- **Speed Control**: 0.5x to 2.0x playback speed

#### Audio Features
- **Vocabulary Preview**: Brief overview of all new words and their meanings at the beginning of TTS
- **Sentence-by-sentence playback**
- **Word highlighting during audio**
- **Pronunciation practice mode**
- **Audio-only learning sessions**

## Technical Implementation

### Technology Stack

#### Frontend
- **Framework**: React Native / Flutter for cross-platform
- **State Management**: Redux/Zustand
- **Audio**: React Native Sound / AudioPlayers
- **UI Components**: Native Base / Material Design
- **Word Interaction**: Clickable word overlays with definition popups
- **Highlighting**: Visual emphasis for replaced vocabulary words

#### Backend
- **Runtime**: Node.js / Python FastAPI
- **Database**: PostgreSQL + Redis (caching)
- **Authentication**: JWT with refresh tokens
- **API Design**: RESTful with GraphQL consideration

#### External Integrations
- **News APIs**: NewsAPI, Reuters API, Associated Press
- **AI/LLM**: OpenAI GPT-4, Anthropic Claude, or Google Gemini
- **TTS**: Google Cloud Text-to-Speech, AWS Polly
- **Infrastructure**: AWS/GCP with CDN for audio files

### Database Schema

#### Core Tables
```sql
-- Users and profiles
users (id, email, created_at, last_active)
user_profiles (user_id, learning_goal, daily_target, preferences)

-- Vocabulary management
vocabulary_lists (id, name, description, difficulty_level)
words (id, word, definition, pronunciation, difficulty, examples, simplified_chinese_definition)
list_words (list_id, word_id, priority)
word_stems (word_id, stem, lemma) -- For stemming-based matching

-- Learning progress
user_words (user_id, word_id, status, next_review, interval, ease_factor)
learning_sessions (id, user_id, article_id, started_at, completed_at)
word_encounters (session_id, word_id, correct, response_time)

-- Content management
articles (id, title, content, source, published_date, difficulty, content_type)
article_words (article_id, word_id, position, original_word)
generated_articles (id, target_words, generation_prompt, review_status)
```

### API Design

#### Core Endpoints
```
GET /api/user/profile - Get user profile and preferences
POST /api/user/assessment - Submit vocabulary assessment
GET /api/vocabulary/lists - Available vocabulary lists
GET /api/learning/daily-article - Get today's personalized article
POST /api/learning/session - Submit learning session results
GET /api/learning/progress - Get learning analytics
GET /api/audio/article/{id} - Get article audio file
POST /api/content/generate-article - Trigger AI article generation for specific words
GET /api/content/article-types - Get available content types (news/generated)
```

## Development Phases
(TODO: I re wrote this section entirely, please undersatnd and update the previous part accordingly)

### Phase 0: Prototpye

### Phase 0.1: Voacb service
(TODO: improve this section)
This phase is mainly focus on core algorithm, for any input paragraph:
- word difficutly classification: stemming first, and then use vocab based classification. This is the first pass, we might make some mistake, don't worry we will have a AI pass to check again later
- this vocab based classification is the key to user personalisation, e.g. differnet user can have their own 'known'/'unknown' vocab, we should have a Vocab service:
```
we have different set of vocab list:
# e.g. the common vocab list (e.g. TOEFL, CET4, stop-word vocab) etc.
# The common vocab is large (a few thousands word), could be persist in the serivce memory
# the common vocab should be ordered and exlcusive, e.g. Elementray vocab < Middle School < CET4 < TOEFL < GRE
stop_words_vocab = Vocab.load(Vocab.STOP_WORDS)
toefl_vocab = Vocab.load(Vocab.TOEFL)


# e.g. also containinig user's customised known and unknown vocab list, could be adjusted dynamically
# this is small vocab can be dynamically load/unload per user request
user_vocab = Vocab.load(user_id)  # This may require a API call, high IO cost
```

Then with everything, we could start tag each unknown word in the article. The unknown words are
- words in common vocab that is one level lower to user's current level
- exlcuding words explicitly marked as 'known' from user's dict (e.g. user just leant the new TOELF word recently)

With the difficult word tagged, then later we will hand over to AI to substitute

(TODO: in this phase, we don't have a user management system yet, just make a dummy one)


### Phase 0.2: AI-powered vocabulary substitution
(TODO: please expand)

The goal is to for 


### Phase 1: MVP (8-10 weeks)
- User authentication and basic profiles
- Single vocabulary list (TOEFL)
- Manual content creation (10 sample articles)
- Basic spaced repetition
- Simple TTS integration with vocabulary preview
- Core learning flow
- **Target Market**: Chinese-speaking users with Simplified Chinese definitions
- Interactive word highlighting and click-to-define functionality

### Phase 2: Content Automation (6-8 weeks)
- News API integration with content filtering
- AI-powered vocabulary substitution with stemming
- Multiple vocabulary lists
- Enhanced spaced repetition algorithm
- Progress analytics dashboard
- Advanced content safety and political content filtering

### Phase 3: Advanced Features (8-10 weeks)
- Advanced audio features
- Social learning elements
- Offline mode support
- Advanced analytics and insights
- Performance optimizations
- **Internationalization**: Expand beyond Chinese speakers to other native languages

### Phase 4: Scale & Polish (4-6 weeks)
- Production deployment
- Performance monitoring
- User feedback integration
- Content quality improvements
- Platform-specific optimizations

## Success Metrics

### User Engagement
- Daily active users (DAU)
- Session duration average
- Article completion rate
- Learning streak retention

### Learning Effectiveness
- Vocabulary retention rate (7-day, 30-day)
- User-reported vocabulary improvement
- Time to proficiency goals
- Spaced repetition effectiveness

### Product Performance
- Content generation accuracy
- TTS quality ratings
- App performance metrics
- User satisfaction scores

## Risk Mitigation

### Technical Risks
- **AI Content Quality**: Implement multiple validation layers
- **TTS Reliability**: Multiple provider fallbacks
- **Scalability**: Cloud-native architecture with auto-scaling

### Business Risks
- **Content Licensing**: Ensure proper news source agreements
- **Competition**: Focus on unique value proposition
- **User Acquisition**: Leverage content marketing and SEO

### Compliance Considerations
- **Data Privacy**: GDPR and CCPA compliance
- **Content Rights**: Proper attribution and licensing
- **Accessibility**: WCAG 2.1 AA compliance
- **Educational Standards**: Alignment with language learning frameworks

## User Interface Design Considerations

### Interactive Word Features
- **Word Highlighting**: Visually distinguish replaced vocabulary words from original text
- **Click-to-Define**: Tap any highlighted word to view definition popup
- **Definition Display**: Show both English definition and Simplified Chinese translation
- **Progress Indicators**: Visual feedback for word mastery levels

### Content Safety & Filtering
- **Age-Appropriate Content**: Robust filtering for teenage users
- **Political Content Moderation**: Avoid controversial political topics
- **Content Rating System**: Internal classification for content appropriateness
- **Parental Controls**: Optional content restrictions and monitoring

### Localization Strategy
- **Phase 1**: Chinese-speaking users (Simplified Chinese definitions)
- **Future Phases**: Spanish, French, German, Japanese, Korean speakers
- **Cultural Adaptation**: Culturally relevant examples and contexts

## Technical Considerations

### Natural Language Processing
- **Stemming Algorithms**: Porter Stemmer or Snowball Stemmer for English
- **Lemmatization**: Advanced word form reduction for accurate matching
- **Part-of-Speech Tagging**: Ensure grammatically correct substitutions
- **Named Entity Recognition**: Preserve proper nouns and specific terms

### Content Processing Pipeline
```
Raw News Article
       ↓
   Content Safety Filter
       ↓
   Difficulty Analysis (with stemming)
       ↓
   Vocabulary Matching
       ↓
   AI-Powered Substitution
       ↓
   Quality Validation
       ↓
   [If substitution fails] → AI Article Generation
       ↓
   TTS Generation (with vocab preview)
       ↓
   User Delivery
```

### Hybrid Content Strategy

#### News-Based Articles (Primary)
- Real news articles with AI-powered vocabulary substitution
- Maintains relevance and authenticity
- Suitable for words that can be contextually replaced

#### AI-Generated Articles (Secondary)
- **Use Case**: Words with highly specific meanings that cannot be naturally substituted
- **Examples**: Technical terms, specialized vocabulary, domain-specific jargon
- **Content Types**:
  - Fictional news-style articles incorporating target vocabulary
  - Educational scenarios and case studies
  - Historical or cultural narratives
- **Quality Assurance**: Human review for accuracy and appropriateness

## Future Enhancements

- Personalized difficulty adaptation
- Multi-language native speaker support
- Collaborative learning features
- Gamification elements
- Integration with educational platforms
- Advanced analytics and AI insights
- Voice interaction capabilities
- Augmented reality vocabulary exploration
