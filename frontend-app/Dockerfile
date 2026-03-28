FROM node:20-alpine AS build

WORKDIR /app

# Copy packages (vite alias resolves @nexus/ai-bot to this)
COPY packages/ /app/packages/

# Copy frontend source
COPY frontend-app/package.json frontend-app/vite.config.ts frontend-app/tsconfig*.json frontend-app/index.html ./

# Remove workspace refs (resolved by vite alias at build time)
RUN node -e "const p=JSON.parse(require('fs').readFileSync('package.json','utf8')); delete (p.dependencies||{})['@nexus/ai-bot']; delete (p.dependencies||{})['@nexus/bot-admin']; require('fs').writeFileSync('package.json', JSON.stringify(p, null, 2));"

RUN npm install --legacy-peer-deps

COPY frontend-app/src ./src
COPY frontend-app/public ./public

RUN npx vite build

# ── Production: serve with nginx ──
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend-app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
