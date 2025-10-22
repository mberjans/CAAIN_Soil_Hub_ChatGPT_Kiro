# Sample Images for Nutrient Deficiency Detection

This directory contains sample crop images used for testing and validating the nutrient deficiency detection system. These images are essential for development, testing, and demonstration purposes.

## Directory Structure

```
sample_images/
├── README.md                    # This documentation file
└── test_images/                 # Test images for development and testing
    ├── corn_healthy.jpg
    ├── corn_nitrogen_deficiency.jpg
    ├── corn_phosphorus_deficiency.jpg
    ├── corn_potassium_deficiency.jpg
    ├── soybean_healthy.jpg
    ├── soybean_iron_deficiency.jpg
    ├── soybean_nitrogen_deficiency.jpg
    ├── wheat_healthy.jpg
    ├── wheat_nitrogen_deficiency.jpg
    └── wheat_sulfur_deficiency.jpg
```

## Image Categories

### Corn Images
- **corn_healthy.jpg**: Healthy corn plant showing normal green coloration and growth
- **corn_nitrogen_deficiency.jpg**: Corn plant showing nitrogen deficiency symptoms (yellowing of older leaves, stunted growth)
- **corn_phosphorus_deficiency.jpg**: Corn plant showing phosphorus deficiency symptoms (purple/reddish discoloration, poor growth)
- **corn_potassium_deficiency.jpg**: Corn plant showing potassium deficiency symptoms (leaf edge burn, yellowing between veins)

### Soybean Images
- **soybean_healthy.jpg**: Healthy soybean plant with normal leaf coloration
- **soybean_nitrogen_deficiency.jpg**: Soybean plant showing nitrogen deficiency (pale green/yellowing of lower leaves)
- **soybean_iron_deficiency.jpg**: Soybean plant showing iron deficiency (interveinal chlorosis, yellowing between veins)

### Wheat Images
- **wheat_healthy.jpg**: Healthy wheat plant with normal green foliage
- **wheat_nitrogen_deficiency.jpg**: Wheat plant showing nitrogen deficiency (yellowing of older leaves)
- **wheat_sulfur_deficiency.jpg**: Wheat plant showing sulfur deficiency (yellowing of younger leaves)

## Image Specifications

### Technical Requirements
- **Format**: JPEG (recommended for compression) or PNG
- **Minimum Resolution**: 224x224 pixels (for CNN model input)
- **Recommended Resolution**: 640x480 pixels or higher
- **Color Space**: RGB (essential for symptom detection)
- **File Size**: Under 5MB (recommended for web upload)

### Image Quality Guidelines
- **Lighting**: Natural daylight or well-diffused artificial light
- **Focus**: Sharp focus on plant leaves and symptoms
- **Background**: Minimal background noise, focus on plant tissue
- **Scale**: Close-up shots showing leaf detail and symptoms clearly
- **Angle**: Top-down or side angles that clearly show leaf discoloration

## Usage Instructions

### Development Testing
These images are used in the test suite for:
```bash
pytest tests/test_api_integration.py -v
```

### Manual Testing
Test the API manually using curl:
```bash
curl -X POST http://localhost:8004/api/v1/deficiency/image-analysis \
  -F "image=@sample_images/test_images/corn_nitrogen_deficiency.jpg" \
  -F "crop_type=corn" \
  -F "growth_stage=V6"
```

### Model Training
For training improved models, organize images by deficiency type:
```
training_data/
├── corn/
│   ├── healthy/
│   ├── nitrogen_deficiency/
│   ├── phosphorus_deficiency/
│   └── potassium_deficiency/
├── soybean/
│   ├── healthy/
│   ├── nitrogen_deficiency/
│   └── iron_deficiency/
└── wheat/
    ├── healthy/
    ├── nitrogen_deficiency/
    └── sulfur_deficiency/
```

## Deficiency Symptoms Reference

### Nitrogen Deficiency
- **Visual Symptoms**: Yellowing (chlorosis) of older/lower leaves, stunted growth
- **Pattern**: Bottom-up yellowing as nitrogen is mobile in plants
- **Crops Affected**: All major crops (corn, soybean, wheat)

### Phosphorus Deficiency
- **Visual Symptoms**: Purple or reddish discoloration, delayed maturity
- **Pattern**: Dark green to purple coloration, poor root development
- **Crops Affected**: Most severe in corn

### Potassium Deficiency
- **Visual Symptoms**: Yellowing between veins, leaf edge burn/scorching
- **Pattern**: Marginal chlorosis and necrosis
- **Crops Affected**: Particularly visible in corn

### Iron Deficiency
- **Visual Symptoms**: Interveinal chlorosis (yellowing between veins)
- **Pattern**: Young leaves affected first, veins remain green
- **Crops Affected**: Common in soybean, especially in high-pH soils

### Sulfur Deficiency
- **Visual Symptoms**: Yellowing of young leaves
- **Pattern**: Top-down yellowing as sulfur is immobile in plants
- **Crops Affected**: Wheat and other cereals

## Image Sources and Attribution

### Current Images
The sample images in this directory are placeholder images intended for:
- Development testing
- API integration validation
- UI/UX demonstration
- Performance benchmarking

### Production Requirements
For production deployment, obtain images from:
1. **Agricultural Research Institutions**: University extension services
2. **Plant Pathology Databases**: Professional image collections
3. **Field Trials**: Controlled photography showing confirmed deficiencies
4. **Partner Organizations**: Agricultural companies and research bodies

### Image Licensing
Ensure all production images have appropriate licenses:
- Creative Commons (CC BY, CC BY-SA)
- Public Domain
- Commercial licenses with proper attribution
- Custom licenses from agricultural institutions

## Adding New Images

When adding new test images:

1. **Verify Quality**: Ensure images meet technical specifications
2. **Confirm Diagnosis**: Use expert-verified or laboratory-confirmed cases
3. **Update Metadata**: Add image information to this README
4. **Test Integration**: Run full test suite to ensure compatibility
5. **Version Control**: Commit with descriptive commit messages

### Image Metadata Template
```markdown
- **filename.jpg**: [Crop type] - [Deficiency type]
  - Source: [Image source/attribution]
  - Date: [When image was taken/obtained]
  - Location: [Geographic location, if relevant]
  - Growth Stage: [Plant growth stage]
  - Verification: [How deficiency was confirmed]
  - Usage Rights: [License information]
```

## Testing Scenarios

### Basic Functionality Tests
- Verify API can process each image format
- Test with different crop types
- Validate deficiency detection accuracy
- Check quality assessment functionality

### Edge Cases
- Low-quality images (blurry, poor lighting)
- Multiple deficiencies in one image
- Different growth stages
- Various lighting conditions
- Multiple plant parts (leaves, stems, ears)

### Performance Tests
- Processing time per image
- Memory usage during analysis
- Concurrent request handling
- Large file upload handling

## Best Practices

### Image Collection
1. **Consistency**: Use consistent lighting and camera settings
2. **Documentation**: Record growth stage, soil conditions, and treatments
3. **Verification**: Confirm deficiencies through soil/tissue analysis
4. **Diversity**: Include multiple varieties and environmental conditions

### Image Management
1. **Regular Updates**: Add new images as seasons progress
2. **Quality Control**: Periodically review and remove poor-quality images
3. **Backup**: Maintain backups of valuable test images
4. **Version Control**: Track changes to image collections

## Troubleshooting

### Common Issues
- **Poor Detection Results**: Check image quality and clarity
- **Upload Failures**: Verify file format and size limits
- **Memory Issues**: Reduce image resolution for testing
- **False Positives**: Ensure images show clear deficiency symptoms

### Support
For issues with sample images:
1. Check image quality against specifications
2. Verify file format compatibility
3. Test with known working images first
4. Consult the API documentation for proper usage

## Future Enhancements

### Planned Additions
- [ ] Add growth stage-specific examples
- [ ] Include severity progression series
- [ ] Add multiple deficiency examples
- [ ] Include recovery images post-treatment
- [ ] Add different crop varieties

### Community Contributions
Contributions of new test images are welcome. Please ensure:
- Images meet quality standards
- Deficiencies are professionally verified
- Proper attribution and licensing are included
- Images are tested with the current API

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Contact**: For questions or contributions, please create an issue in the project repository.