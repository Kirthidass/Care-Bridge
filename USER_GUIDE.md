# CARE-BRIDGE AI - User Guide

## 🎉 Welcome to CARE-BRIDGE AI

Your personal healthcare report assistant powered by AI.

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Login & Role Selection](#login--role-selection)
3. [Dashboard Overview](#dashboard-overview)
4. [Uploading Reports](#uploading-reports)
5. [Understanding Your Results](#understanding-your-results)
6. [Using the Chat Feature](#using-the-chat-feature)
7. [Managing Documents](#managing-documents)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements

- **Web Browser**: Chrome, Firefox, Edge, or Safari (latest version)
- **Internet Connection**: Required for AI explanations
- **Screen Resolution**: Minimum 1280x720

### Accessing the Application

1. Open your web browser
2. Navigate to: `http://localhost:5173`
3. You should see the CARE-BRIDGE AI login page

---

## Login & Role Selection

### Step 1: Login

On the login page:
- Enter any email address (e.g., `demo@carebridge.ai`)
- Enter any password
- Click "Login"

> **Note**: This is a demo version with simplified authentication.

### Step 2: Select Your Role

Choose your viewing mode:

**👤 Patient Mode**
- Simple, easy-to-understand explanations
- Focus on what results mean for you
- Action items and next steps

**🩺 Clinician Mode**
- Technical medical summaries
- Clinical assessments and recommendations
- Reference ranges and interpretations

---

## Dashboard Overview

### Main Components

```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar      │   Main Content Area    │   Chat Panel       │
│               │                        │                    │
│ • Documents   │  ┌──────────────────┐  │  💬 Ask Questions  │
│ • Lab Reports │  │  Report Details  │  │                    │
│ • Upload      │  │  & Explanations  │  │  Your active       │
│ • Manage      │  └──────────────────┘  │  document chat     │
│ • Logout      │                        │                    │
└─────────────────────────────────────────────────────────────┘
```

### Navigation

- **Documents**: View all your uploaded reports
- **Lab Reports**: Quick access to lab results
- **Upload New Report**: Add a new medical report
- **Manage Documents**: Delete old reports
- **Logout**: Return to login page

---

## Uploading Reports

### Supported File Types

- PDF (`.pdf`)
- PNG Images (`.png`)
- JPEG Images (`.jpg`, `.jpeg`)

### Upload Process

1. Click "📤 Upload New Report" button (sidebar or top-right)
2. Select your medical report file
3. Wait for processing (usually 2-5 seconds)
4. View the automatically generated explanation

### What Happens During Upload

1. **File Storage**: Your file is securely saved
2. **Parsing**: AI extracts test names, values, and ranges
3. **Safety Check**: System identifies abnormal values
4. **Explanation**: AI generates role-appropriate explanation
5. **Display**: Results appear in the main panel

---

## Understanding Your Results

### Test Results Table

Each test result shows:
- **Test Name**: e.g., "Hemoglobin", "WBC", "Glucose"
- **Your Value**: The measured result
- **Normal Range**: Reference values
- **Status Indicator**: 
  - ✓ Green = Normal
  - ⚠ Yellow/Red = Outside normal range

### Example Display

```
┌────────────────────────────────────────────┐
│ Test Results                               │
├────────────────────────────────────────────┤
│ Hemoglobin                                 │
│ Range: 12.0-16.0                           │
│                          12.5 g/dL    ✓    │
├────────────────────────────────────────────┤
│ Glucose                                    │
│ Range: 70-100                              │
│                         105 mg/dL    ⚠     │
└────────────────────────────────────────────┘
```

### AI Explanation Sections

1. **📋 Your Lab Results Summary**
   - Overview of all test results
   - Status of each value
   - What each result means

2. **⚠️ Important Notes**
   - Highlighted abnormal values
   - Immediate attention items
   - Safety warnings

3. **📅 Contextual Information**
   - Report age and relevance
   - Timeline considerations
   - Follow-up recommendations

4. **⚠️ Disclaimer**
   - Not medical advice
   - Consult healthcare provider
   - Source citations

---

## Using the Chat Feature

### Starting a Chat

1. Select a report from your document list
2. Look for the chat panel on the right side
3. Type your question in the input field
4. Press Enter or click the send button (➤)

### Example Questions

**For Patients:**
- "What does my glucose level mean?"
- "Should I be worried about my hemoglobin?"
- "What is WBC and why is mine high?"
- "Do I need to see a doctor?"

**For Clinicians:**
- "Provide differential for elevated glucose"
- "Compare with age-adjusted norms"
- "Suggest follow-up tests"
- "Clinical significance of findings"

### Chat Tips

- ✅ Be specific about which test you're asking about
- ✅ Ask one question at a time
- ✅ Reference actual values from your report
- ❌ Don't ask for diagnosis or treatment plans
- ❌ Don't share personal identifiable information

---

## Managing Documents

### Viewing All Documents

1. Navigate to "Manage Documents" from sidebar
2. See table with:
   - Report Name
   - Upload Date
   - Report Type
   - Actions

### Deleting Documents

1. Go to "Manage Documents"
2. Find the report you want to delete
3. Click the "🗑️ Delete" button
4. Confirm deletion in the popup
5. Document is permanently removed

> **Note**: Deletion cannot be undone!

### Document Auto-Sync

- Changes in Manage Documents automatically update Dashboard
- Deleted reports are removed from all views
- No manual refresh needed

---

## Troubleshooting

### Common Issues

#### "No Reports Yet" Message

**Problem**: Dashboard shows empty state
**Solution**: 
- Upload a new report
- Check if documents were accidentally deleted
- Verify backend server is running

#### Upload Failed

**Problem**: File upload doesn't work
**Solution**:
- Check file format (PDF, PNG, JPG only)
- Verify file size < 10MB
- Ensure backend server is running
- Check browser console for errors

#### Chat Not Responding

**Problem**: Chat messages don't get replies
**Solution**:
- Select a report first
- Wait 3-5 seconds for processing
- Check backend logs for errors
- Reload the page

#### Deleted Document Still Showing

**Problem**: Document appears after deletion
**Solution**:
- Navigate away and back to Dashboard
- Hard refresh browser (Ctrl+F5)
- Clear browser cache

### Browser Issues

#### Page Not Loading

1. Check URL is `http://localhost:5173`
2. Verify frontend server is running
3. Clear browser cache
4. Try incognito/private mode

#### Styling Looks Wrong

1. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check browser console for CSS errors

### Server Issues

#### Backend Not Responding

1. Check terminal running `python main.py`
2. Verify port 8000 is not in use
3. Check for Python errors in terminal
4. Restart backend server

#### Frontend Not Loading

1. Check terminal running `npm run dev`
2. Verify port 5173 is available
3. Try `npm install` again
4. Restart frontend server

---

## Best Practices

### Security

- ✅ Use secure network connection
- ✅ Don't share login credentials
- ✅ Log out when finished
- ✅ Don't upload real patient data (demo only)

### Usage

- ✅ Upload clear, readable reports
- ✅ Review all disclaimers
- ✅ Consult healthcare provider for medical decisions
- ✅ Keep documents organized

### Privacy

- ⚠️ **Important**: This is a demo application
- ⚠️ Don't upload actual medical records with real patient information
- ⚠️ Use synthetic or de-identified data only
- ⚠️ Data is stored locally on your machine

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Upload Report | `Ctrl + U` |
| Focus Chat | `Ctrl + /` |
| Logout | `Ctrl + L` |
| Close Modal | `Esc` |

---

## Getting Help

### Technical Support

- Check server logs in terminal windows
- Review browser console (F12) for errors
- Consult README.md for setup instructions
- Check troubleshooting section above

### Medical Questions

⚠️ **Important**: CARE-BRIDGE AI is not a substitute for professional medical advice.

For medical questions:
- Consult your healthcare provider
- Visit a medical clinic
- Call emergency services if urgent (911)

---

## Feature Highlights

### ✨ What Makes CARE-BRIDGE AI Special

1. **Role-Aware Intelligence**
   - Adapts explanations to your role
   - Patient-friendly or clinician-technical

2. **Safety First**
   - Automatic abnormal value detection
   - Clear warnings and disclaimers
   - Non-diagnostic explanations only

3. **Interactive Learning**
   - Ask follow-up questions
   - Get contextual answers
   - Reference medical guidelines

4. **Modern UX**
   - Clean, intuitive interface
   - Real-time updates
   - Mobile-responsive design

5. **Document Management**
   - Upload multiple reports
   - Compare over time
   - Easy deletion

---

## Version Information

- **Version**: 1.0.0 (Demo)
- **Last Updated**: January 10, 2026
- **Platform**: Web Application
- **Backend**: FastAPI + Python
- **Frontend**: React + Vite

---

## Feedback

This is a demonstration project. For a production deployment:

- Add real authentication
- Implement database storage
- Add user management
- Enable HIPAA compliance
- Integrate with EHR systems
- Add mobile apps

---

**Remember**: Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.

🏥 **CARE-BRIDGE AI** - Making Healthcare Information Accessible

