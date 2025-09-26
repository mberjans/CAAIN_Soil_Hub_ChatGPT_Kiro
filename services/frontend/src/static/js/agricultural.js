// AFAS Agricultural JavaScript Functions

class AgriculturalCalculator {
    constructor() {
        this.soilHealthWeights = {
            ph: 0.25,
            organicMatter: 0.25,
            phosphorus: 0.2,
            potassium: 0.2,
            texture: 0.1
        };
    }

    // Calculate soil health score
    calculateSoilHealthScore(soilData) {
        let score = 0;
        
        // pH scoring (optimal 6.0-7.0)
        const ph = parseFloat(soilData.ph);
        if (ph >= 6.0 && ph <= 7.0) {
            score += 10 * this.soilHealthWeights.ph;
        } else if (ph >= 5.5 && ph <= 7.5) {
            score += 8 * this.soilHealthWeights.ph;
        } else if (ph >= 5.0 && ph <= 8.0) {
            score += 6 * this.soilHealthWeights.ph;
        } else {
            score += 3 * this.soilHealthWeights.ph;
        }
        
        // Organic matter scoring (optimal >3%)
        const om = parseFloat(soilData.organicMatter);
        if (om >= 4.0) {
            score += 10 * this.soilHealthWeights.organicMatter;
        } else if (om >= 3.0) {
            score += 8 * this.soilHealthWeights.organicMatter;
        } else if (om >= 2.0) {
            score += 6 * this.soilHealthWeights.organicMatter;
        } else {
            score += 3 * this.soilHealthWeights.organicMatter;
        }
        
        // Phosphorus scoring (optimal 20-40 ppm)
        const p = parseInt(soilData.phosphorus);
        if (p >= 20 && p <= 40) {
            score += 10 * this.soilHealthWeights.phosphorus;
        } else if (p >= 15 && p <= 50) {
            score += 8 * this.soilHealthWeights.phosphorus;
        } else if (p >= 10 && p <= 60) {
            score += 6 * this.soilHealthWeights.phosphorus;
        } else {
            score += 3 * this.soilHealthWeights.phosphorus;
        }
        
        // Potassium scoring (optimal 150-250 ppm)
        const k = parseInt(soilData.potassium);
        if (k >= 150 && k <= 250) {
            score += 10 * this.soilHealthWeights.potassium;
        } else if (k >= 100 && k <= 300) {
            score += 8 * this.soilHealthWeights.potassium;
        } else if (k >= 75 && k <= 350) {
            score += 6 * this.soilHealthWeights.potassium;
        } else {
            score += 3 * this.soilHealthWeights.potassium;
        }
        
        // Texture bonus (loam types get bonus)
        const texture = soilData.texture;
        if (['loam', 'silt_loam', 'clay_loam'].includes(texture)) {
            score += 10 * this.soilHealthWeights.texture;
        } else if (['sandy_loam'].includes(texture)) {
            score += 8 * this.soilHealthWeights.texture;
        } else {
            score += 6 * this.soilHealthWeights.texture;
        }
        
        return Math.min(score, 10);
    }

    // Calculate nitrogen rate for corn
    calculateNitrogenRate(cropData) {
        const yieldGoal = parseInt(cropData.yieldGoal);
        const organicMatter = parseFloat(cropData.organicMatter);
        const previousCrop = cropData.previousCrop;
        const soilTestN = parseInt(cropData.soilTestN || 0);
        
        // Base nitrogen rate (lbs N per bushel)
        let nRate = yieldGoal * 0.9;
        
        // Previous crop credit
        let legumeCreditN = 0;
        if (previousCrop === 'soybean') {
            legumeCreditN = 40;
        } else if (previousCrop === 'alfalfa') {
            legumeCreditN = 60;
        }
        
        // Soil test credit (rough conversion)
        const soilTestCreditN = soilTestN * 2;
        
        // Organic matter credit
        let omCreditN = 0;
        if (organicMatter > 4.0) {
            omCreditN = 20;
        } else if (organicMatter > 3.0) {
            omCreditN = 10;
        }
        
        // Calculate final rate
        const finalRate = Math.max(nRate - legumeCreditN - soilTestCreditN - omCreditN, 80);
        
        return {
            totalNRate: Math.round(finalRate),
            legumeCreditN: legumeCreditN,
            soilTestCreditN: soilTestCreditN,
            organicMatterCreditN: omCreditN,
            baseRate: Math.round(nRate)
        };
    }

    // Calculate fertilizer costs
    calculateFertilizerCosts(rates, prices, acres) {
        const nCost = (rates.nitrogen * acres * prices.urea) / (2000 * 0.46); // Urea is 46% N
        const pCost = (rates.phosphorus * acres * prices.dap) / (2000 * 0.46); // DAP is 46% P2O5
        const kCost = (rates.potassium * acres * prices.potash) / (2000 * 0.60); // Potash is 60% K2O
        
        return {
            nitrogen: Math.round(nCost),
            phosphorus: Math.round(pCost),
            potassium: Math.round(kCost),
            total: Math.round(nCost + pCost + kCost)
        };
    }

    // Calculate ROI
    calculateROI(costs, revenue) {
        return ((revenue - costs.total) / costs.total) * 100;
    }
}

// Utility functions
class AgriculturalUtils {
    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    static formatPercentage(value, decimals = 0) {
        return `${value.toFixed(decimals)}%`;
    }

    static validateSoilPH(ph) {
        const phValue = parseFloat(ph);
        if (isNaN(phValue) || phValue < 3.0 || phValue > 10.0) {
            return { valid: false, message: 'pH must be between 3.0 and 10.0' };
        }
        if (phValue < 4.5) {
            return { valid: true, warning: 'Extremely acidic soil - lime application recommended' };
        }
        if (phValue > 8.5) {
            return { valid: true, warning: 'Very alkaline soil - may limit nutrient availability' };
        }
        return { valid: true };
    }

    static validateNutrientLevel(value, nutrient) {
        const numValue = parseInt(value);
        const ranges = {
            phosphorus: { min: 0, max: 200, optimal: [20, 40] },
            potassium: { min: 0, max: 800, optimal: [150, 250] },
            organicMatter: { min: 0, max: 15, optimal: [3, 5] }
        };
        
        const range = ranges[nutrient];
        if (!range) return { valid: true };
        
        if (isNaN(numValue) || numValue < range.min || numValue > range.max) {
            return { valid: false, message: `${nutrient} must be between ${range.min} and ${range.max}` };
        }
        
        if (numValue < range.optimal[0]) {
            return { valid: true, warning: `${nutrient} is below optimal range` };
        }
        
        return { valid: true };
    }

    static animateProgressBar(element, targetWidth, duration = 1000) {
        let start = 0;
        const startTime = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentWidth = start + (targetWidth - start) * progress;
            element.style.width = `${currentWidth}%`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }

    static showLoadingState(button) {
        const spinner = button.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'inline-block';
            button.disabled = true;
        }
    }

    static hideLoadingState(button) {
        const spinner = button.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'none';
            button.disabled = false;
        }
    }

    static displayAlert(message, type = 'info', container = null) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        if (container) {
            container.appendChild(alertDiv);
        } else {
            document.body.insertBefore(alertDiv, document.body.firstChild);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Form validation
class AgriculturalFormValidator {
    constructor() {
        this.utils = new AgriculturalUtils();
    }

    validateSoilTestForm(formData) {
        const errors = [];
        const warnings = [];
        
        // Validate pH
        const phValidation = AgriculturalUtils.validateSoilPH(formData.ph);
        if (!phValidation.valid) {
            errors.push(phValidation.message);
        } else if (phValidation.warning) {
            warnings.push(phValidation.warning);
        }
        
        // Validate nutrients
        ['phosphorus', 'potassium'].forEach(nutrient => {
            const validation = AgriculturalUtils.validateNutrientLevel(formData[nutrient], nutrient);
            if (!validation.valid) {
                errors.push(validation.message);
            } else if (validation.warning) {
                warnings.push(validation.warning);
            }
        });
        
        // Validate organic matter
        const om = parseFloat(formData.organicMatter);
        if (isNaN(om) || om < 0 || om > 15) {
            errors.push('Organic matter must be between 0% and 15%');
        } else if (om < 2.0) {
            warnings.push('Low organic matter - consider cover crops or compost');
        }
        
        return { errors, warnings, valid: errors.length === 0 };
    }

    validateCropSelectionForm(formData) {
        const errors = [];
        
        if (!formData.location || formData.location.trim().length < 3) {
            errors.push('Please provide a valid location');
        }
        
        if (!formData.farm_size || parseInt(formData.farm_size) < 1) {
            errors.push('Farm size must be at least 1 acre');
        }
        
        // Validate soil data
        const soilValidation = this.validateSoilTestForm(formData);
        errors.push(...soilValidation.errors);
        
        return { errors, valid: errors.length === 0 };
    }
}

// Initialize agricultural calculator and utilities
const agCalculator = new AgriculturalCalculator();
const agUtils = new AgriculturalUtils();
const agValidator = new AgriculturalFormValidator();

// pH-Specific Calculation Functions
class PHCalculations {
    static calculateLimeRequirement(currentPh, targetPh, soilTexture, organicMatter, fieldSize) {
        // Buffer pH estimation if not provided
        const bufferPh = this.estimateBufferPh(currentPh, soilTexture, organicMatter);
        
        // Calculate ENR (Effective Neutralizing Requirement)
        const phDifference = targetPh - currentPh;
        let baseRate = 0;
        
        // Base lime rate calculation using buffer pH method
        if (bufferPh <= 6.0) {
            baseRate = 3.0; // tons per acre
        } else if (bufferPh <= 6.5) {
            baseRate = 2.0;
        } else if (bufferPh <= 7.0) {
            baseRate = 1.0;
        } else {
            baseRate = 0.5;
        }
        
        // Adjust for soil texture
        const textureMultiplier = this.getTextureMultiplier(soilTexture);
        baseRate *= textureMultiplier;
        
        // Adjust for organic matter
        const omMultiplier = this.getOrganicMatterMultiplier(organicMatter);
        baseRate *= omMultiplier;
        
        // Adjust for pH difference
        baseRate *= Math.max(phDifference / 1.0, 0.5);
        
        const totalTons = baseRate * fieldSize;
        
        return {
            ratePerAcre: Math.round(baseRate * 10) / 10,
            totalTons: Math.round(totalTons * 10) / 10,
            bufferPh: bufferPh
        };
    }

    static estimateBufferPh(currentPh, soilTexture, organicMatter) {
        // Simplified buffer pH estimation
        let bufferPh = currentPh - 0.5;
        
        // Adjust based on soil texture (clay holds more buffer)
        if (['clay', 'clay_loam'].includes(soilTexture)) {
            bufferPh -= 0.2;
        } else if (['sand', 'loamy_sand'].includes(soilTexture)) {
            bufferPh += 0.2;
        }
        
        // Adjust based on organic matter
        if (organicMatter > 4.0) {
            bufferPh -= 0.3;
        } else if (organicMatter < 2.0) {
            bufferPh += 0.2;
        }
        
        return Math.max(Math.min(bufferPh, 7.5), 4.0);
    }

    static getTextureMultiplier(soilTexture) {
        const multipliers = {
            'sand': 0.8,
            'loamy_sand': 0.9,
            'sandy_loam': 1.0,
            'loam': 1.1,
            'silt_loam': 1.2,
            'clay_loam': 1.3,
            'clay': 1.4
        };
        return multipliers[soilTexture] || 1.0;
    }

    static getOrganicMatterMultiplier(organicMatter) {
        if (organicMatter > 5.0) return 1.3;
        if (organicMatter > 3.0) return 1.1;
        if (organicMatter > 2.0) return 1.0;
        return 0.9;
    }

    static classifyPhStatus(phValue, cropType = null) {
        const optimal = this.getCropOptimalPh(cropType);
        
        if (phValue >= optimal.min && phValue <= optimal.max) {
            return { status: 'optimal', description: 'Optimal pH range for crop production' };
        } else if (phValue < 4.5) {
            return { status: 'critical', description: 'Extremely acidic - immediate lime application needed' };
        } else if (phValue < 5.5) {
            return { status: 'acidic', description: 'Acidic soil - lime application recommended' };
        } else if (phValue > 8.5) {
            return { status: 'critical', description: 'Very alkaline - may require soil amendment' };
        } else if (phValue > 7.5) {
            return { status: 'alkaline', description: 'Alkaline soil - monitor nutrient availability' };
        } else {
            return { status: 'good', description: 'Acceptable pH range' };
        }
    }

    static getCropOptimalPh(cropType) {
        const cropRanges = {
            'corn': { min: 6.0, max: 7.0 },
            'soybean': { min: 6.0, max: 7.0 },
            'wheat': { min: 6.0, max: 7.5 },
            'alfalfa': { min: 6.8, max: 7.5 },
            'canola': { min: 6.0, max: 7.0 },
            'barley': { min: 6.5, max: 7.5 },
            'oats': { min: 6.0, max: 7.0 },
            'peas': { min: 6.0, max: 7.5 },
            'potatoes': { min: 5.8, max: 6.5 },
            'blueberries': { min: 4.5, max: 5.5 }
        };
        
        return cropRanges[cropType] || { min: 6.0, max: 7.0 };
    }

    static calculateNutrientAvailability(phValue) {
        const nutrients = {
            nitrogen: this.getNutrientAvailability(phValue, [6.0, 8.0]),
            phosphorus: this.getNutrientAvailability(phValue, [6.5, 7.5]),
            potassium: this.getNutrientAvailability(phValue, [6.0, 8.5]),
            calcium: this.getNutrientAvailability(phValue, [6.5, 8.5]),
            magnesium: this.getNutrientAvailability(phValue, [6.0, 8.5]),
            sulfur: this.getNutrientAvailability(phValue, [6.0, 8.0]),
            iron: this.getNutrientAvailability(phValue, [4.0, 6.5]),
            manganese: this.getNutrientAvailability(phValue, [5.0, 6.5]),
            zinc: this.getNutrientAvailability(phValue, [5.0, 7.0]),
            copper: this.getNutrientAvailability(phValue, [5.0, 7.0]),
            boron: this.getNutrientAvailability(phValue, [5.0, 7.5]),
            molybdenum: this.getNutrientAvailability(phValue, [6.5, 8.5])
        };
        
        return nutrients;
    }

    static getNutrientAvailability(phValue, optimalRange) {
        const [min, max] = optimalRange;
        
        if (phValue >= min && phValue <= max) {
            return { level: 'high', percentage: 90, description: 'Optimal availability' };
        } else if (phValue >= min - 0.5 && phValue <= max + 0.5) {
            return { level: 'medium', percentage: 70, description: 'Good availability' };
        } else if (phValue >= min - 1.0 && phValue <= max + 1.0) {
            return { level: 'low', percentage: 50, description: 'Reduced availability' };
        } else {
            return { level: 'very_low', percentage: 30, description: 'Poor availability' };
        }
    }

    static generatePhRecommendations(phValue, cropType, soilTexture, organicMatter) {
        const recommendations = [];
        const status = this.classifyPhStatus(phValue, cropType);
        const optimal = this.getCropOptimalPh(cropType);
        
        if (status.status === 'critical' && phValue < 5.0) {
            recommendations.push('Immediate lime application required - soil is extremely acidic');
            recommendations.push('Consider split lime application over 2 seasons');
            recommendations.push('Retest soil in 6 months after lime application');
        } else if (status.status === 'acidic') {
            const limeReq = this.calculateLimeRequirement(phValue, optimal.min, soilTexture, organicMatter, 1);
            recommendations.push(`Apply ${limeReq.ratePerAcre} tons of agricultural lime per acre`);
            recommendations.push('Incorporate lime within 2 weeks of application');
        } else if (status.status === 'alkaline') {
            recommendations.push('Monitor iron and zinc availability in crops');
            recommendations.push('Consider sulfur application to lower pH gradually');
            recommendations.push('Use acidifying fertilizers (ammonium sulfate)');
        } else if (status.status === 'critical' && phValue > 8.5) {
            recommendations.push('Severe alkalinity - consult soil specialist');
            recommendations.push('Consider gypsum application for calcium without raising pH');
            recommendations.push('Use chelated micronutrients for deficiency prevention');
        } else if (status.status === 'optimal') {
            recommendations.push('pH is in optimal range - maintain current practices');
            recommendations.push('Continue regular soil testing every 2-3 years');
        }
        
        // Additional organic matter recommendations
        if (organicMatter < 3.0) {
            recommendations.push('Increase organic matter with cover crops or compost');
        }
        
        return recommendations;
    }
}

// pH-Specific Validation Functions
class PHValidation {
    static validatePhInput(phValue) {
        const ph = parseFloat(phValue);
        
        if (isNaN(ph)) {
            return { valid: false, message: 'pH must be a valid number' };
        }
        
        if (ph < 3.0 || ph > 12.0) {
            return { valid: false, message: 'pH must be between 3.0 and 12.0' };
        }
        
        if (ph < 4.0) {
            return { valid: true, warning: 'Extremely low pH - verify measurement' };
        }
        
        if (ph > 9.0) {
            return { valid: true, warning: 'Very high pH - verify measurement' };
        }
        
        return { valid: true };
    }

    static validateLimeCalculationInputs(data) {
        const errors = [];
        
        // Validate current pH
        const phValidation = this.validatePhInput(data.currentPh);
        if (!phValidation.valid) {
            errors.push('Current pH: ' + phValidation.message);
        }
        
        // Validate target pH
        const targetPhValidation = this.validatePhInput(data.targetPh);
        if (!targetPhValidation.valid) {
            errors.push('Target pH: ' + targetPhValidation.message);
        }
        
        // Check if target pH is higher than current
        if (data.targetPh <= data.currentPh) {
            errors.push('Target pH must be higher than current pH');
        }
        
        // Validate field size
        if (!data.fieldSize || data.fieldSize <= 0) {
            errors.push('Field size must be greater than 0');
        }
        
        // Validate organic matter
        if (data.organicMatter < 0 || data.organicMatter > 15) {
            errors.push('Organic matter must be between 0% and 15%');
        }
        
        return { valid: errors.length === 0, errors };
    }
}

// Add pH calculations to existing utils
AgriculturalUtils.PHCalculations = PHCalculations;
AgriculturalUtils.PHValidation = PHValidation;

// Export for use in other scripts
window.AgriculturalCalculator = AgriculturalCalculator;
window.AgriculturalUtils = AgriculturalUtils;
window.AgriculturalFormValidator = AgriculturalFormValidator;
window.PHCalculations = PHCalculations;
window.PHValidation = PHValidation;
window.agCalculator = agCalculator;
window.agUtils = agUtils;
window.agValidator = agValidator;