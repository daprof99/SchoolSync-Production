# SchoolSync 2.0 Dashboard

Beautiful admin portal built with Next.js, TypeScript, and Tailwind CSS.

## Features
- 📊 Real-time revenue & debtor analytics
- 📈 Interactive charts (Recharts)
- 💬 Message inbox
- 📤 Results upload interface
- 📢 Broadcast messaging

## Setup

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Build for Production

```bash
npm run build
npm start
```

## Deploy to Vercel

```bash
npm install -g vercel
vercel
```

## Configuration

The dashboard proxies API requests to your Python backend running on `http://localhost:14031`.

Update `next.config.js` if your backend runs on a different port.

## Customization

- **Colors**: Edit `app/globals.css`
- **Components**: Add to `components/` directory
- **API calls**: Use `axios` from `app/page.tsx`

---

Built with modern web technologies for blazing fast performance ⚡
