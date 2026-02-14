# Vercel Blob Storage Configuration

This website uses Vercel Blob Storage to serve database deliverable JSON files. The API routes (`/api/deliverable/[id]` and `/api/metadata/[id]`) attempt to fetch files from blob storage first, then fall back to the local filesystem.

## Configuration

### Local Development

1. Create a `.env.local` file in the `apps/website/` directory:

```bash
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_Ad7SZ62s8LD9MQvS_EjMhBn3tnZz5WoYJFKLaxt3rPZbSey
```

2. Verify configuration:

```bash
npm run verify-blob
```

### Vercel Deployment

1. Go to your Vercel project dashboard
2. Navigate to **Settings** > **Environment Variables**
3. Add:
   - **Name**: `BLOB_READ_WRITE_TOKEN`
   - **Value**: Your blob storage token (starts with `vercel_blob_`)
   - **Environment**: Production, Preview, Development (as needed)

4. Redeploy your application

## Token Format

The token should start with `vercel_blob_` and have the format:
```
vercel_blob_rw_<random_string>
```

## How It Works

1. **API Routes** (`/api/deliverable/[id]` and `/api/metadata/[id]`):
   - First attempt: Fetch from Vercel Blob Storage using the token
   - Fallback: Read from local filesystem (`client/db/` directory)

2. **Blob Storage Path**:
   - Base path: `guides/`
   - File pattern: `guides/db-{N}_deliverable.json`
   - Example: `guides/db-6_deliverable.json`

## Troubleshooting

### Token Not Found

If you see "BLOB_READ_WRITE_TOKEN not configured":
- Check that `.env.local` exists and contains the token
- Verify the token is set in Vercel dashboard (for production)
- Run `npm run verify-blob` to check configuration

### Blob Not Found

If blob storage returns 404:
- The file might not be uploaded to blob storage yet
- The API will automatically fall back to local filesystem
- This is expected behavior for local development

### Testing

Test blob storage configuration:
```bash
npm run verify-blob
```

Test API endpoints:
```bash
# Start dev server
npm run dev

# In another terminal, test endpoints
curl http://localhost:3000/api/deliverable/db6
curl http://localhost:3000/api/metadata/db6
```

## Security Notes

- **Never commit** `.env.local` to version control (already in `.gitignore`)
- **Never commit** tokens to version control
- Use Vercel dashboard for production environment variables
- Rotate tokens if compromised
