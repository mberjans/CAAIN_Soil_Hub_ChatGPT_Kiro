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

// Export for use in other scripts
window.AgriculturalCalculator = AgriculturalCalculator;
window.AgriculturalUtils = AgriculturalUtils;
window.AgriculturalFormValidator = AgriculturalFormValidator;
window.agCalculator = agCalculator;
window.agUtils = agUtils;
window.agValidator = agValidator;