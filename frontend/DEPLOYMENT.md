# Deploying Sentinel Scan to Cloudflare Pages

This guide covers deploying the Sentinel Scan landing page to Cloudflare Pages with the custom domain `sentinelscan.app`.

## Prerequisites

- Cloudflare account
- Domain `sentinelscan.app` added to your Cloudflare account
- GitHub repository with the code

## Method 1: Deploy via Cloudflare Dashboard (Recommended)

### Step 1: Connect GitHub Repository

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **Pages** in the left sidebar
3. Click **Create a project**
4. Click **Connect to Git**
5. Select your GitHub repository: `Cody-Lange/Regulatory-Scanner`
6. Click **Begin setup**

### Step 2: Configure Build Settings

Set the following build configuration:

```
Project name: sentinel-scan
Production branch: main (or your default branch)
Framework preset: Vite
Build command: npm run build
Build output directory: dist
Root directory: frontend
```

**Important:** Set the **Root directory** to `frontend` since that's where the landing page lives.

### Step 3: Environment Variables

No environment variables needed for this static site.

### Step 4: Deploy

1. Click **Save and Deploy**
2. Cloudflare will build and deploy your site
3. You'll get a `*.pages.dev` URL (e.g., `sentinel-scan.pages.dev`)

### Step 5: Configure Custom Domain

1. In the Cloudflare Pages dashboard, go to your project
2. Click **Custom domains** tab
3. Click **Set up a custom domain**
4. Enter: `sentinelscan.app`
5. Click **Continue**
6. Cloudflare will automatically configure DNS (since your domain is on Cloudflare)
7. Also add `www.sentinelscan.app` and configure redirect to apex domain

**DNS will be configured automatically** since the domain is already in your Cloudflare account.

## Method 2: Deploy via Wrangler CLI

### Install Wrangler

```bash
npm install -g wrangler
```

### Login to Cloudflare

```bash
wrangler login
```

### Deploy from Frontend Directory

```bash
cd frontend
npm run build
npx wrangler pages deploy dist --project-name=sentinel-scan
```

### Set Up Custom Domain (via CLI)

```bash
wrangler pages domain add sentinel-scan sentinelscan.app
```

## Build Configuration Details

### Package.json Scripts

The `package.json` already includes the necessary build script:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }
}
```

### Node Version

The `.node-version` file specifies Node 20, which Cloudflare Pages will use automatically.

### Build Output

- Framework: Vite
- Output directory: `dist/`
- Static assets are optimized and ready for production

## Post-Deployment Tasks

### 1. Update DNS (if needed)

If you want to add subdomains or configure email:

1. Go to DNS settings in Cloudflare
2. Add records as needed:
   - `A` record: `@` → Cloudflare Pages IP (auto-configured)
   - `CNAME` record: `www` → `sentinelscan.app` (for www redirect)

### 2. Configure SSL/TLS

1. In Cloudflare dashboard → SSL/TLS
2. Set encryption mode to **Full** (recommended) or **Full (strict)**
3. Enable **Always Use HTTPS**
4. Enable **Automatic HTTPS Rewrites**

### 3. Configure Page Rules (Optional)

Set up redirects and caching:

1. Go to **Page Rules**
2. Create rule: `www.sentinelscan.app/*` → `https://sentinelscan.app/$1` (301 redirect)

### 4. Enable Analytics

1. Go to **Analytics** tab in Cloudflare Pages
2. Enable Web Analytics for free visitor insights

## Performance Optimizations

Cloudflare Pages automatically provides:

- **Global CDN** - Content served from 275+ locations
- **Brotli/Gzip compression** - Automatically compressed assets
- **HTTP/3 support** - Fastest protocol
- **Automatic HTTPS** - Free SSL certificate
- **DDoS protection** - Built-in security
- **Instant cache invalidation** - New deploys clear cache immediately

## Continuous Deployment

Every push to your production branch will trigger an automatic deployment:

1. Push to `main` (or configured production branch)
2. Cloudflare automatically builds and deploys
3. New version goes live in ~1 minute
4. Preview deployments for pull requests

## Preview Deployments

Every pull request gets a unique preview URL:

- Format: `<commit-hash>.sentinel-scan.pages.dev`
- Test changes before merging
- Share previews with stakeholders

## Troubleshooting

### Build Fails

Check that:
- Root directory is set to `frontend`
- Build command is `npm run build`
- Node version is compatible (v18+)

### Custom Domain Not Working

1. Verify domain is in Cloudflare account
2. Check DNS records are configured
3. Wait 5-10 minutes for DNS propagation
4. Clear browser cache

### Site Not Updating

1. Check deployment logs in Cloudflare Pages dashboard
2. Verify you pushed to the correct branch
3. Try manual deploy: `wrangler pages deploy dist`

## Monitoring

### View Deployment History

1. Cloudflare Pages dashboard
2. Click **View build log** for any deployment
3. See commit message, build time, deploy status

### Analytics

- Cloudflare Web Analytics (free)
- Page views, unique visitors, bandwidth
- No cookies, GDPR compliant

## Cost

Cloudflare Pages is **FREE** for:
- Unlimited sites
- Unlimited requests
- Unlimited bandwidth
- 500 builds/month (more than enough)
- Custom domains
- SSL certificates

## Next Steps

1. Deploy the site following Method 1 above
2. Configure custom domain `sentinelscan.app`
3. Enable SSL/TLS settings
4. Set up www redirect
5. Enable analytics
6. Test the site at `https://sentinelscan.app`

Your landing page will be live at:
- **Primary:** https://sentinelscan.app
- **Preview:** https://sentinel-scan.pages.dev

## Support

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Community](https://community.cloudflare.com/)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
