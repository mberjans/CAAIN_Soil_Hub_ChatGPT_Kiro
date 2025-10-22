# Model Training Guide

## Overview

This guide covers training, evaluating, and improving machine learning models for nutrient deficiency detection in the CAAIN Soil Hub Image Analysis Service. The service uses Convolutional Neural Networks (CNNs) to detect nutrient deficiencies in corn, soybean, and wheat crops from images.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Data Collection](#data-collection)
3. [Data Preparation](#data-preparation)
4. [Model Architecture](#model-architecture)
5. [Training Pipeline](#training-pipeline)
6. [Evaluation Metrics](#evaluation-metrics)
7. [Hyperparameter Tuning](#hyperparameter-tuning)
8. [Model Deployment](#model-deployment)
9. [Continuous Improvement](#continuous-improvement)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements

- **GPU**: NVIDIA GPU with at least 8GB VRAM (recommended for training)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB+ for datasets and models
- **CPU**: Multi-core processor for data preprocessing

### Software Requirements

```bash
# Required Python packages (in addition to requirements.txt)
tensorflow==2.14.0
opencv-python==4.8.1.78
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
pandas==2.1.0
albumentations==1.3.1
tqdm==4.66.1
```

### Environment Setup

```bash
# Activate virtual environment
cd services/image-analysis
source venv/bin/activate

# Install additional training dependencies
pip install scikit-learn matplotlib seaborn pandas albumentations tqdm

# Verify GPU availability (optional but recommended)
python -c "import tensorflow as tf; print(f'GPU Available: {len(tf.config.list_physical_devices(\"GPU\")) > 0}')"
```

## Data Collection

### Image Requirements

1. **Minimum Resolution**: 224x224 pixels
2. **Format**: JPEG or PNG
3. **Quality**: Clear, well-lit images with minimal blur
4. **Content**: Focus on plant leaves showing deficiency symptoms

### Deficiency Classes

#### Corn (Zea mays)
- **Healthy**: No visible deficiency symptoms
- **Nitrogen (N)**: Yellowing of older leaves, stunted growth
- **Phosphorus (P)**: Purple/reddish leaves, delayed maturity
- **Potassium (K)**: Leaf edge burn, yellowing between veins
- **Sulfur (S)**: Yellowing of young leaves
- **Iron (Fe)**: Interveinal chlorosis in young leaves
- **Zinc (Zn)**: White or yellow bands, shortened internodes

#### Soybean (Glycine max)
- **Healthy**: No visible deficiency symptoms
- **Nitrogen (N)**: Pale green leaves, reduced growth
- **Phosphorus (P)**: Dark green leaves with purple tints
- **Potassium (K)**: Chlorotic leaf margins, necrosis
- **Iron (Fe)**: Interveinal chlorosis
- **Manganese (Mn)**: Interveinal chlorosis with brown spots

#### Wheat (Triticum aestivum)
- **Healthy**: No visible deficiency symptoms
- **Nitrogen (N)**: Yellowing from leaf tips downward
- **Phosphorus (P)**: Dark green foliage, purpling
- **Potassium (K)**: Leaf scorch, weak straw
- **Sulfur (S)**: Yellowing of young leaves

### Data Sources

1. **Field Collection**: Systematic photography from research plots
2. **Research Partnerships**: Agricultural universities and extensions
3. **Public Datasets**: PlantVillage, PlantDoc, CropDoc
4. **Synthetic Data**: Augmented images for rare deficiencies

### Data Collection Guidelines

```python
# Sample collection script structure
import os
import json
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

def collect_metadata(image_path, crop_type, deficiency_type, growth_stage, location):
    """Collect comprehensive metadata for training images"""
    metadata = {
        "image_path": image_path,
        "crop_type": crop_type,
        "deficiency_type": deficiency_type,
        "growth_stage": growth_stage,
        "location": location,
        "date_collected": datetime.now().isoformat(),
        "photographer": "expert_name",
        "weather_conditions": {
            "lighting": "sunny/partly_cloudy/cloudy",
            "time_of_day": "morning/afternoon/evening"
        },
        "camera_settings": get_exif_data(image_path),
        "plant_part": "leaf/stem/whole_plant",
        "severity_rating": "mild/moderate/severe",  # Expert rating
        "verified_by": "expert_name",
        "quality_score": calculate_quality_score(image_path)
    }
    return metadata
```

## Data Preparation

### Directory Structure

```
dataset/
├── train/
│   ├── corn/
│   │   ├── healthy/
│   │   ├── nitrogen/
│   │   ├── phosphorus/
│   │   └── potassium/
│   ├── soybean/
│   │   └── ...
│   └── wheat/
│       └── ...
├── validation/
│   └── ... (same structure as train)
├── test/
│   └── ... (same structure as train)
└── metadata/
    ├── train_labels.csv
    ├── validation_labels.csv
    └── test_labels.csv
```

### Data Preprocessing Pipeline

```python
import cv2
import numpy as np
from albumentations import Compose, RandomRotate90, Flip, Rotate, GaussNoise
from albumentations import RandomBrightnessContrast, HueSaturationValue
import tensorflow as tf

class DataPreprocessor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.train_augment = Compose([
            RandomRotate90(p=0.5),
            Flip(p=0.5),
            Rotate(limit=15, p=0.3),
            GaussNoise(p=0.2),
            RandomBrightnessContrast(p=0.3),
            HueSaturationValue(p=0.3)
        ])
        self.val_augment = None  # No augmentation for validation/test

    def preprocess_image(self, image_path, is_training=True):
        """Load and preprocess a single image"""
        # Read image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize
        image = cv2.resize(image, self.target_size)

        # Apply augmentation if training
        if is_training:
            augmented = self.train_augment(image=image)
            image = augmented['image']

        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0

        return image

    def create_dataset(self, df, batch_size=32, is_training=True):
        """Create TensorFlow dataset from dataframe"""
        def generator():
            for _, row in df.iterrows():
                image = self.preprocess_image(row['image_path'], is_training)
                label = row['label']
                yield image, label

        dataset = tf.data.Dataset.from_generator(
            generator,
            output_signature=(
                tf.TensorSpec(shape=(*self.target_size, 3), dtype=tf.float32),
                tf.TensorSpec(shape=(), dtype=tf.int32)
            )
        )

        if is_training:
            dataset = dataset.shuffle(1000)

        dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
        return dataset
```

### Data Quality Control

```python
def validate_image_quality(image_path):
    """Validate image meets quality standards"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return False, "Cannot read image"

        # Check resolution
        height, width = image.shape[:2]
        if width < 224 or height < 224:
            return False, "Resolution too low"

        # Check blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 100:
            return False, "Image too blurry"

        # Check brightness
        brightness = np.mean(image)
        if brightness < 50 or brightness > 200:
            return False, "Poor lighting"

        return True, "Valid image"

    except Exception as e:
        return False, f"Error: {str(e)}"

def clean_dataset(dataset_path):
    """Remove invalid images from dataset"""
    invalid_images = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(root, file)
                is_valid, message = validate_image_quality(image_path)
                if not is_valid:
                    invalid_images.append((image_path, message))
                    os.remove(image_path)

    return invalid_images
```

## Model Architecture

### Base CNN Architecture

```python
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks

def create_base_model(input_shape=(224, 224, 3), num_classes=7):
    """Create base CNN model for deficiency detection"""

    inputs = layers.Input(shape=input_shape)

    # Convolutional Block 1
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # Convolutional Block 2
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # Convolutional Block 3
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # Convolutional Block 4
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # Dense layers
    x = layers.Flatten()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)

    # Output layer
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs=inputs, outputs=outputs)
    return model
```

### Transfer Learning Option

```python
def create_transfer_model(input_shape=(224, 224, 3), num_classes=7, base_model_name='EfficientNetB0'):
    """Create transfer learning model using pre-trained backbone"""

    # Choose base model
    if base_model_name == 'EfficientNetB0':
        base_model = tf.keras.applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
    elif base_model_name == 'ResNet50':
        base_model = tf.keras.applications.ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
    elif base_model_name == 'MobileNetV2':
        base_model = tf.keras.applications.MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )

    # Freeze base model initially
    base_model.trainable = False

    # Build model
    inputs = layers.Input(shape=input_shape)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs=inputs, outputs=outputs)
    return model, base_model
```

## Training Pipeline

### Training Script

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class ModelTrainer:
    def __init__(self, crop_type, config):
        self.crop_type = crop_type
        self.config = config
        self.model = None
        self.history = None

    def prepare_data(self, dataset_path):
        """Load and prepare training data"""
        # Load metadata
        df = pd.read_csv(f"{dataset_path}/metadata/train_labels.csv")

        # Filter by crop type
        df = df[df['crop_type'] == self.crop_type]

        # Create label mapping
        self.label_to_int = {label: i for i, label in enumerate(df['deficiency_type'].unique())}
        self.int_to_label = {i: label for label, i in self.label_to_int.items()}
        df['label'] = df['deficiency_type'].map(self.label_to_int)

        # Split data
        train_df, val_df = train_test_split(
            df, test_size=0.2, stratify=df['label'], random_state=42
        )

        return train_df, val_df

    def create_model(self, num_classes):
        """Create and compile model"""
        if self.config['use_transfer_learning']:
            self.model, self.base_model = create_transfer_model(
                num_classes=num_classes,
                base_model_name=self.config['base_model']
            )
        else:
            self.model = create_base_model(num_classes=num_classes)

        # Compile model
        optimizer = optimizers.Adam(
            learning_rate=self.config['learning_rate'],
            weight_decay=self.config['weight_decay']
        )

        self.model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', 'top_5_accuracy']
        )

        return self.model

    def setup_callbacks(self):
        """Setup training callbacks"""
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            callbacks.ModelCheckpoint(
                f'models/{self.crop_type}_deficiency_best.h5',
                monitor='val_accuracy',
                save_best_only=True
            ),
            callbacks.CSVLogger(f'models/{self.crop_type}_training_log.csv')
        ]

        return callbacks_list

    def train(self, train_df, val_df):
        """Train the model"""
        # Create datasets
        preprocessor = DataPreprocessor()
        train_dataset = preprocessor.create_dataset(
            train_df,
            batch_size=self.config['batch_size'],
            is_training=True
        )
        val_dataset = preprocessor.create_dataset(
            val_df,
            batch_size=self.config['batch_size'],
            is_training=False
        )

        # Setup callbacks
        callbacks_list = self.setup_callbacks()

        # Train model
        self.history = self.model.fit(
            train_dataset,
            epochs=self.config['epochs'],
            validation_data=val_dataset,
            callbacks=callbacks_list,
            verbose=1
        )

        return self.history

    def fine_tune(self, train_df, val_df):
        """Fine-tune transfer learning model"""
        if not hasattr(self, 'base_model'):
            print("No base model for fine-tuning")
            return

        # Unfreeze top layers of base model
        self.base_model.trainable = True

        # Freeze all layers except top 20
        for layer in self.base_model.layers[:-20]:
            layer.trainable = False

        # Recompile with lower learning rate
        self.model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-5),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', 'top_5_accuracy']
        )

        # Continue training
        self.history = self.model.fit(
            train_dataset,
            epochs=self.config['fine_tune_epochs'],
            validation_data=val_dataset,
            callbacks=callbacks_list,
            verbose=1
        )
```

### Training Configuration

```python
# Training configuration
training_config = {
    # Data parameters
    'batch_size': 32,
    'target_size': (224, 224),

    # Model parameters
    'use_transfer_learning': True,
    'base_model': 'EfficientNetB0',  # 'EfficientNetB0', 'ResNet50', 'MobileNetV2'

    # Training parameters
    'epochs': 50,
    'fine_tune_epochs': 20,
    'learning_rate': 1e-3,
    'weight_decay': 1e-4,

    # Augmentation parameters
    'augmentation_prob': 0.7,
    'rotation_range': 15,
    'brightness_range': 0.2
}

# Crop-specific configurations
crop_configs = {
    'corn': {
        'num_classes': 7,  # healthy + 6 deficiencies
        'class_weights': {0: 1.0, 1: 1.5, 2: 1.2, 3: 1.3, 4: 1.4, 5: 1.6, 6: 1.8}
    },
    'soybean': {
        'num_classes': 6,  # healthy + 5 deficiencies
        'class_weights': {0: 1.0, 1: 1.4, 2: 1.2, 3: 1.3, 4: 1.5, 5: 1.6}
    },
    'wheat': {
        'num_classes': 5,  # healthy + 4 deficiencies
        'class_weights': {0: 1.0, 1: 1.3, 2: 1.2, 3: 1.4, 4: 1.5}
    }
}
```

## Evaluation Metrics

### Comprehensive Evaluation

```python
class ModelEvaluator:
    def __init__(self, model, label_mapping):
        self.model = model
        self.label_mapping = label_mapping

    def evaluate_on_test_set(self, test_df):
        """Comprehensive evaluation on test set"""
        preprocessor = DataPreprocessor()
        test_dataset = preprocessor.create_dataset(
            test_df,
            batch_size=32,
            is_training=False
        )

        # Get predictions
        y_true = []
        y_pred = []
        y_pred_proba = []

        for images, labels in test_dataset:
            predictions = self.model.predict(images, verbose=0)
            y_true.extend(labels.numpy())
            y_pred.extend(np.argmax(predictions, axis=1))
            y_pred_proba.extend(predictions)

        # Calculate metrics
        report = classification_report(
            y_true, y_pred,
            target_names=list(self.label_mapping.keys()),
            output_dict=True
        )

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        # Per-class metrics
        class_metrics = {}
        for i, class_name in enumerate(self.label_mapping.keys()):
            class_metrics[class_name] = {
                'precision': report[class_name]['precision'],
                'recall': report[class_name]['recall'],
                'f1_score': report[class_name]['f1-score'],
                'support': report[class_name]['support']
            }

        return {
            'overall_accuracy': report['accuracy'],
            'macro_avg': report['macro avg'],
            'weighted_avg': report['weighted avg'],
            'class_metrics': class_metrics,
            'confusion_matrix': cm
        }

    def plot_confusion_matrix(self, cm, class_names):
        """Plot confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names
        )
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig('evaluation/confusion_matrix.png', dpi=300)
        plt.close()

    def analyze_predictions(self, test_df, save_misclassified=True):
        """Analyze prediction quality and confidence"""
        misclassified = []
        low_confidence = []

        preprocessor = DataPreprocessor()

        for _, row in test_df.iterrows():
            image = preprocessor.preprocess_image(row['image_path'], is_training=False)
            image_batch = np.expand_dims(image, axis=0)

            prediction = self.model.predict(image_batch, verbose=0)[0]
            predicted_class = np.argmax(prediction)
            confidence = np.max(prediction)
            true_class = row['label']

            if predicted_class != true_class:
                misclassified.append({
                    'image_path': row['image_path'],
                    'true_class': self.label_mapping[true_class],
                    'predicted_class': self.label_mapping[predicted_class],
                    'confidence': confidence,
                    'all_probabilities': prediction.tolist()
                })

            if confidence < 0.7:  # Low confidence threshold
                low_confidence.append({
                    'image_path': row['image_path'],
                    'true_class': self.label_mapping[true_class],
                    'predicted_class': self.label_mapping[predicted_class],
                    'confidence': confidence
                })

        return misclassified, low_confidence
```

## Hyperparameter Tuning

### Automated Hyperparameter Search

```python
import keras_tuner as kt
from tensorflow.keras import layers, models

class DeficiencyModelHyperModel(kt.HyperModel):
    def __init__(self, input_shape, num_classes):
        self.input_shape = input_shape
        self.num_classes = num_classes

    def build(self, hp):
        """Build model with hyperparameters"""
        inputs = layers.Input(shape=self.input_shape)

        # Hyperparameters to tune
        num_blocks = hp.Int('num_blocks', 3, 5)
        initial_filters = hp.Choice('initial_filters', [32, 64, 128])
        dropout_rate = hp.Float('dropout_rate', 0.1, 0.5, step=0.1)
        learning_rate = hp.Choice('learning_rate', [1e-4, 1e-3, 1e-2])

        x = inputs

        # Build variable number of convolutional blocks
        filters = initial_filters
        for i in range(num_blocks):
            x = layers.Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.MaxPooling2D((2, 2))(x)
            x = layers.Dropout(dropout_rate)(x)
            filters *= 2

        # Dense layers
        x = layers.Flatten()(x)
        x = layers.Dense(
            hp.Int('dense_units', 128, 512, step=128),
            activation='relu'
        )(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(dropout_rate)(x)
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)

        model = models.Model(inputs=inputs, outputs=outputs)

        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

def run_hyperparameter_tuning(train_df, val_df, crop_type):
    """Run automated hyperparameter tuning"""
    preprocessor = DataPreprocessor()

    # Create datasets
    train_dataset = preprocessor.create_dataset(train_df, is_training=True)
    val_dataset = preprocessor.create_dataset(val_df, is_training=False)

    # Initialize hypermodel
    hypermodel = DeficiencyModelHyperModel(
        input_shape=(224, 224, 3),
        num_classes=len(train_df['label'].unique())
    )

    # Initialize tuner
    tuner = kt.Hyperband(
        hypermodel,
        objective='val_accuracy',
        max_epochs=30,
        factor=3,
        directory='tuning',
        project_name=f'{crop_type}_deficiency_tuning'
    )

    # Define early stopping
    stop_early = callbacks.EarlyStopping(monitor='val_loss', patience=5)

    # Run search
    tuner.search(
        train_dataset,
        validation_data=val_dataset,
        callbacks=[stop_early]
    )

    # Get best hyperparameters
    best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

    print(f"""
    Hyperparameter tuning results for {crop_type}:
    Optimal number of blocks: {best_hps.get('num_blocks')}
    Optimal initial filters: {best_hps.get('initial_filters')}
    Optimal dropout rate: {best_hps.get('dropout_rate')}
    Optimal learning rate: {best_hps.get('learning_rate')}
    Optimal dense units: {best_hps.get('dense_units')}
    """)

    return best_hps
```

## Model Deployment

### Model Conversion for Production

```python
def convert_model_for_production(model_path, crop_type):
    """Convert trained model for production deployment"""

    # Load trained model
    model = tf.keras.models.load_model(model_path)

    # Convert to TensorFlow Lite for edge deployment
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Quantize model for smaller size
    converter.target_spec.supported_types = [tf.float16]

    tflite_model = converter.convert()

    # Save TFLite model
    tflite_path = f"models/{crop_type}_deficiency_quantized.tflite"
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)

    # Save model metadata
    metadata = {
        "crop_type": crop_type,
        "model_version": "1.0",
        "input_shape": model.input_shape,
        "output_classes": len(model.output_shape),
        "model_size_mb": os.path.getsize(tflite_path) / (1024 * 1024),
        "date_created": datetime.now().isoformat()
    }

    with open(f"models/{crop_type}_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Model converted and saved to {tflite_path}")
    return tflite_path

def test_converted_model(tflite_path, test_image_path):
    """Test converted TFLite model"""
    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Load and preprocess test image
    preprocessor = DataPreprocessor()
    input_image = preprocessor.preprocess_image(test_image_path, is_training=False)
    input_image = np.expand_dims(input_image, axis=0).astype(np.float32)

    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], input_image)

    # Run inference
    interpreter.invoke()

    # Get output
    predictions = interpreter.get_tensor(output_details[0]['index'])

    return predictions[0]
```

### Model Versioning

```python
import shutil
import json
from datetime import datetime

class ModelRegistry:
    def __init__(self, registry_path="model_registry"):
        self.registry_path = registry_path
        os.makedirs(registry_path, exist_ok=True)

    def register_model(self, model_path, crop_type, performance_metrics, metadata=None):
        """Register a new model version"""
        # Generate version ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"{crop_type}_v{timestamp}"

        # Create version directory
        version_dir = os.path.join(self.registry_path, version_id)
        os.makedirs(version_dir, exist_ok=True)

        # Copy model file
        model_filename = os.path.basename(model_path)
        shutil.copy2(model_path, os.path.join(version_dir, model_filename))

        # Create model card
        model_card = {
            "version_id": version_id,
            "crop_type": crop_type,
            "model_file": model_filename,
            "performance_metrics": performance_metrics,
            "metadata": metadata or {},
            "registration_date": datetime.now().isoformat(),
            "status": "staged"  # staged -> production -> deprecated
        }

        # Save model card
        with open(os.path.join(version_dir, "model_card.json"), 'w') as f:
            json.dump(model_card, f, indent=2)

        # Update registry index
        self._update_registry_index(model_card)

        print(f"Model registered as {version_id}")
        return version_id

    def _update_registry_index(self, model_card):
        """Update the registry index file"""
        index_file = os.path.join(self.registry_path, "registry_index.json")

        # Load existing index
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {"models": []}

        # Add new model
        index["models"].append(model_card)

        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
```

## Continuous Improvement

### Performance Monitoring

```python
class ModelMonitor:
    def __init__(self, model_path, crop_type):
        self.model_path = model_path
        self.crop_type = crop_type
        self.model = tf.keras.models.load_model(model_path)
        self.performance_log = []

    def log_prediction(self, image_path, true_label=None, predicted_label=None, confidence=None):
        """Log individual prediction for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "true_label": true_label,
            "predicted_label": predicted_label,
            "confidence": confidence,
            "model_version": os.path.basename(self.model_path)
        }

        self.performance_log.append(log_entry)

    def analyze_performance_drift(self, window_size=1000):
        """Analyze if model performance is drifting"""
        if len(self.performance_log) < window_size:
            return None

        recent_logs = self.performance_log[-window_size:]

        # Calculate accuracy in recent window
        correct_predictions = sum(
            1 for log in recent_logs
            if log['true_label'] is not None and log['predicted_label'] == log['true_label']
        )

        recent_accuracy = correct_predictions / len(recent_logs)

        # Compare with baseline (first window)
        baseline_logs = self.performance_log[:window_size]
        baseline_correct = sum(
            1 for log in baseline_logs
            if log['true_label'] is not None and log['predicted_label'] == log['true_label']
        )
        baseline_accuracy = baseline_correct / len(baseline_logs)

        drift = baseline_accuracy - recent_accuracy

        return {
            "baseline_accuracy": baseline_accuracy,
            "recent_accuracy": recent_accuracy,
            "drift": drift,
            "requires_retraining": drift > 0.1  # 10% drop threshold
        }

    def identify_edge_cases(self, confidence_threshold=0.7):
        """Identify cases where model is uncertain"""
        edge_cases = [
            log for log in self.performance_log
            if log['confidence'] is not None and log['confidence'] < confidence_threshold
        ]

        return edge_cases
```

### Active Learning Pipeline

```python
class ActiveLearningPipeline:
    def __init__(self, model, data_manager):
        self.model = model
        self.data_manager = data_manager
        self.candidate_pool = []

    def select_uncertain_samples(self, unlabeled_data, n_samples=100):
        """Select samples with highest uncertainty for labeling"""
        uncertainties = []

        for data_point in unlabeled_data:
            # Get model prediction
            image = self.data_manager.preprocess_image(data_point['image_path'])
            image_batch = np.expand_dims(image, axis=0)

            predictions = self.model.predict(image_batch, verbose=0)[0]

            # Calculate uncertainty (entropy)
            entropy = -np.sum(predictions * np.log(predictions + 1e-8))

            uncertainties.append({
                'image_path': data_point['image_path'],
                'uncertainty': entropy,
                'predictions': predictions.tolist()
            })

        # Sort by uncertainty and select top samples
        uncertainties.sort(key=lambda x: x['uncertainty'], reverse=True)
        return uncertainties[:n_samples]

    def update_model_with_new_labels(self, newly_labeled_data):
        """Update model with newly labeled data"""
        # Combine with existing training data
        combined_data = self.data_manager.combine_with_training_data(newly_labeled_data)

        # Retrain model (can use partial fitting or full retraining)
        # This is a simplified example - in practice you'd use more sophisticated updating
        trainer = ModelTrainer(self.crop_type, training_config)
        trainer.model = self.model  # Continue from current weights

        history = trainer.fine_tune(combined_data['train'], combined_data['validation'])

        return history
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Overfitting
**Symptoms**: High training accuracy, low validation accuracy

**Solutions**:
```python
# Increase dropout
layers.Dropout(0.5)  # Increase from 0.25

# Add data augmentation
augmentations = Compose([
    RandomRotate90(p=0.7),
    Flip(p=0.7),
    RandomBrightnessContrast(p=0.5),
    GaussNoise(p=0.3)
])

# Add L2 regularization
from tensorflow.keras import regularizers
layers.Conv2D(32, (3, 3), activation='relu',
              kernel_regularizer=regularizers.l2(0.001))

# Early stopping
callbacks.EarlyStopping(monitor='val_loss', patience=15)
```

#### 2. Class Imbalance
**Symptoms**: Poor performance on minority classes

**Solutions**:
```python
# Calculate class weights
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

# Use in training
model.fit(
    train_dataset,
    class_weight=dict(enumerate(class_weights))
)

# Oversample minority classes
from imblearn.over_sampling import RandomOverSampler
ros = RandomOverSampler(random_state=42)
X_resampled, y_resampled = ros.fit_resample(X, y)
```

#### 3. Poor Convergence
**Symptoms**: Loss not decreasing, unstable training

**Solutions**:
```python
# Learning rate scheduling
lr_schedule = optimizers.schedules.ExponentialDecay(
    initial_learning_rate=1e-2,
    decay_steps=1000,
    decay_rate=0.9
)

# Use batch normalization
layers.BatchNormalization()

# Gradient clipping
optimizer = optimizers.Adam(
    learning_rate=1e-3,
    clipnorm=1.0
)
```

#### 4. Memory Issues
**Symptoms**: Out of memory errors during training

**Solutions**:
```python
# Reduce batch size
batch_size = 16  # Reduce from 32

# Use gradient accumulation
accumulation_steps = 4

# Use mixed precision training
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Use data generator instead of loading all data
def data_generator():
    while True:
        for batch in get_batches():
            yield batch
```

### Performance Optimization Checklist

- [ ] **Data Quality**: All images pass quality checks
- [ ] **Class Balance**: Handle imbalanced classes appropriately
- [ ] **Augmentation**: Appropriate data augmentation applied
- [ ] **Architecture**: Model complexity matches dataset size
- [ ] **Learning Rate**: Appropriate learning rate schedule
- [ ] **Regularization**: Proper dropout and weight decay
- [ ] **Batch Size**: Optimal batch size for hardware
- [ ] **Monitoring**: Track training and validation metrics
- [ ] **Early Stopping**: Prevent overfitting
- [ ] **Cross-validation**: Validate model generalization

## Training Schedule

### Recommended Training Pipeline

1. **Data Collection (2-4 weeks)**
   - Gather at least 1000 images per class
   - Ensure balanced representation
   - Collect metadata consistently

2. **Data Preparation (1 week)**
   - Clean and validate dataset
   - Apply quality filters
   - Split into train/validation/test

3. **Initial Training (1-2 weeks)**
   - Train baseline model
   - Establish performance metrics
   - Identify issues early

4. **Hyperparameter Tuning (1-2 weeks)**
   - Automated search for optimal parameters
   - Test different architectures
   - Optimize for specific metrics

5. **Model Evaluation (1 week)**
   - Comprehensive testing on holdout set
   - Error analysis
   - Edge case identification

6. **Production Deployment (3-5 days)**
   - Model conversion and optimization
   - Integration testing
   - Performance validation

7. **Monitoring and Updates (Ongoing)**
   - Track model performance in production
   - Collect feedback data
   - Schedule regular retraining

## Resources

### Datasets
- [PlantVillage](https://plantvillage.psu.edu/)
- [PlantDoc](https://github.com/pratik-090/PlantDoc-Dataset)
- [CropDoc](https://www.cropdoc.org/)
- [IPAD](https://ipad.fbk.eu/) - Image-based Plant Disease Database

### Research Papers
- [Deep Learning for Plant Disease Detection](https://arxiv.org/abs/2004.10827)
- [Survey on Plant Disease Detection](https://doi.org/10.1016/j.compag.2021.106215)
- [Computer Vision in Agriculture](https://doi.org/10.1016/j.compag.2020.105367)

### Tools and Frameworks
- [TensorFlow](https://www.tensorflow.org/)
- [Keras Tuner](https://keras.io/keras_tuner/)
- [Albumentations](https://albumentations.ai/)
- [Weights & Biases](https://wandb.ai/) - Experiment tracking

---

**Last Updated**: October 2024
**Version**: 1.0
**Maintainer**: CAAIN Soil Hub Team

For questions or support, contact the machine learning team at ml-team@caain.org.