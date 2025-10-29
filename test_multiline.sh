#!/bin/bash
# Example script showing how to handle multi-line text with gTTS API

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:8088/api/v1/tts"

echo "Testing multi-line text with gTTS API"
echo "======================================"
echo ""

# Test 1: Simple multi-line English text
echo "Test 1: Simple multi-line English..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"First line.\nSecond line.\nThird line.", "lang":"en"}' \
  --output test1_multiline_en.mp3 \
  --silent

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Success: test1_multiline_en.mp3${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 2: Swedish job description
echo "Test 2: Swedish job description..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"Planera, designa och genomföra manuella tester utifrån krav och användarflöden.\nBygga, underhålla och vidareutveckla automatiserade testsviter API- UI- och regressionstester.\nBidra till teststrategi och testmetodik i teamet.\nSamarbeta med verksamhet för att förstå affärslogik, riskflöden och regulatoriska krav.\nRapportera testresultat fel och förbättringsförslag.\nStötta teamet i att etablera shift-left testing och kvalitetsmedveten utveckling", "lang":"sv"}' \
  --output test2_job_description_sv.mp3 \
  --silent

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Success: test2_job_description_sv.mp3${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 3: List with bullet points
echo "Test 3: English list with bullet points..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"My tasks include:\n• Planning and designing tests\n• Building automated test suites\n• Contributing to test strategy\n• Collaborating with stakeholders\n• Reporting test results", "lang":"en"}' \
  --output test3_list_en.mp3 \
  --silent

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Success: test3_list_en.mp3${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

echo "======================================"
echo "All tests completed!"
echo ""
echo "Generated files:"
ls -lh test*.mp3 2>/dev/null || echo "No files generated"

