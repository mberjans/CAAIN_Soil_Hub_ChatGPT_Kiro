#!/usr/bin/env python3
"""
Setup script for NLP dependencies in the Question Router service.

This script downloads required spaCy models and NLTK data.
"""

import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_spacy_model():
    """Download and install spaCy English model."""
    try:
        logger.info("Downloading spaCy English model...")
        
        # Try to download the small English model first
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Successfully downloaded en_core_web_sm model")
            return True
        else:
            logger.warning(f"Failed to download en_core_web_sm: {result.stderr}")
            
            # Try medium model as fallback
            logger.info("Trying to download en_core_web_md model...")
            result = subprocess.run([
                sys.executable, "-m", "spacy", "download", "en_core_web_md"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Successfully downloaded en_core_web_md model")
                return True
            else:
                logger.error(f"Failed to download en_core_web_md: {result.stderr}")
                return False
                
    except Exception as e:
        logger.error(f"Error downloading spaCy model: {e}")
        return False

def setup_nltk_data():
    """Download required NLTK data."""
    try:
        import nltk
        
        logger.info("Downloading NLTK data...")
        
        # Download required NLTK datasets
        datasets = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'omw-1.4']
        
        for dataset in datasets:
            try:
                logger.info(f"Downloading NLTK dataset: {dataset}")
                nltk.download(dataset, quiet=True)
            except Exception as e:
                logger.warning(f"Failed to download {dataset}: {e}")
        
        logger.info("NLTK data setup completed")
        return True
        
    except ImportError:
        logger.error("NLTK not installed. Please install with: pip install nltk")
        return False
    except Exception as e:
        logger.error(f"Error setting up NLTK data: {e}")
        return False

def verify_installation():
    """Verify that NLP components are working."""
    try:
        # Test spaCy
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp("This is a test sentence for agricultural question classification.")
            logger.info("spaCy en_core_web_sm model loaded successfully")
        except OSError:
            try:
                nlp = spacy.load("en_core_web_md")
                doc = nlp("This is a test sentence for agricultural question classification.")
                logger.info("spaCy en_core_web_md model loaded successfully")
            except OSError:
                logger.error("No spaCy English model available")
                return False
        
        # Test NLTK
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        
        # Test tokenization
        tokens = word_tokenize("This is a test sentence.")
        logger.info(f"NLTK tokenization working: {len(tokens)} tokens")
        
        # Test stopwords
        stop_words = stopwords.words('english')
        logger.info(f"NLTK stopwords loaded: {len(stop_words)} words")
        
        # Test lemmatizer
        lemmatizer = WordNetLemmatizer()
        lemma = lemmatizer.lemmatize("running", "v")
        logger.info(f"NLTK lemmatization working: 'running' -> '{lemma}'")
        
        # Test scikit-learn
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer()
        logger.info("scikit-learn TfidfVectorizer available")
        
        logger.info("All NLP components verified successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying installation: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("Starting NLP setup for Question Router service...")
    
    success = True
    
    # Setup spaCy
    if not install_spacy_model():
        logger.warning("spaCy model installation failed - service will use fallback methods")
        success = False
    
    # Setup NLTK
    if not setup_nltk_data():
        logger.warning("NLTK data setup failed - service will use fallback methods")
        success = False
    
    # Verify installation
    if not verify_installation():
        logger.warning("NLP component verification failed - some features may not work")
        success = False
    
    if success:
        logger.info("NLP setup completed successfully!")
        logger.info("The Question Router service is ready to use advanced NLP features.")
    else:
        logger.warning("NLP setup completed with warnings.")
        logger.info("The Question Router service will work but may have reduced accuracy.")
        logger.info("To fix issues, ensure you have internet connectivity and sufficient disk space.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)