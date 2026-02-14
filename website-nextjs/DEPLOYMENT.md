# Deployment Guide

## Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Vercel Deployment

### Option 1: Vercel Dashboard (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial Next.js app"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Import in Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js
   - Click "Deploy"

3. **Configure Environment Variables (Optional):**
   - Add `NEXT_PUBLIC_VERCEL_ANALYTICS_ID` if using custom analytics

### Option 2: Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Follow prompts:**
   - Link to existing project or create new
   - Confirm settings
   - Deploy

## Build & Test Locally

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Updating Content

To update database content:

1. **Regenerate content JSON:**
   ```bash
   cd /path/to/db
   python3 -c "
   import re
   import json
   from pathlib import Path
   
   html_file = Path('website/index.html')
   content = html_file.read_text(encoding='utf-8')
   
   main_match = re.search(r'<main class=\"main-content\">(.*?)</main>', content, re.DOTALL)
   if main_match:
       main_content = main_match.group(1)
       databases = {}
       for db_num in range(6, 16):
           db_id = f'db{db_num}'
           section_match = re.search(
               rf'<!-- {db_id.upper()} Content -->\s*<div id=\"{db_id}-section\">(.*?)</div>\s*(?=<!--|$)',
               main_content,
               re.DOTALL
           )
           if section_match:
               databases[db_id] = section_match.group(1).strip()
       
       output_file = Path('website-nextjs/lib/database-content.json')
       with open(output_file, 'w', encoding='utf-8') as f:
           json.dump(databases, f, ensure_ascii=False, indent=2)
   "
   ```

2. **Rebuild and redeploy:**
   ```bash
   npm run build
   vercel --prod
   ```

## Troubleshooting

### Build Errors

- **TypeScript errors:** Run `npm run build` to see specific errors
- **Missing dependencies:** Run `npm install`
- **Content not loading:** Check `lib/database-content.json` exists

### Runtime Errors

- **Prism.js not highlighting:** Check browser console for script loading errors
- **Navigation not working:** Check browser console for JavaScript errors
- **Styles not applying:** Verify `globals.css` is imported in `layout.tsx`

## Performance Optimization

- Content is statically generated at build time
- Large JSON file (~2.5MB) is loaded client-side
- Consider code splitting for very large content sections
- Enable Vercel Edge caching for faster loads

## Security Headers

Security headers are configured in `vercel.json`:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
