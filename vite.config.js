import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import compression from 'vite-plugin-compression';
import fs from 'fs';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Middleware plugin: decode incoming media paths and serve files directly
    {
      name: 'vite-decode-media-middleware',
      configureServer(server) {
        server.middlewares.use(async (req, res, next) => {
          try {
            if (!req.url) return next();
            const urlPath = req.url.split('?')[0];
            if (!urlPath.startsWith('/media/')) return next();
            // Try to decode URL path safely
            let decoded;
            try { decoded = decodeURIComponent(urlPath); } catch (e) { decoded = urlPath; }

            // Map to public directory
            const publicRoot = path.join(process.cwd(), 'public');
            const fsPath = path.join(publicRoot, decoded.replace(/^\//, ''));
            if (fs.existsSync(fsPath) && fs.statSync(fsPath).isFile()) {
              const ext = path.extname(fsPath).toLowerCase().slice(1);
              const mime = {
                mp4: 'video/mp4',
                webm: 'video/webm',
                mov: 'video/quicktime',
                jpg: 'image/jpeg',
                jpeg: 'image/jpeg',
                png: 'image/png',
              }[ext] || 'application/octet-stream';
              res.setHeader('Content-Type', mime);
              res.setHeader('Cache-Control', 'no-cache');
              const stream = fs.createReadStream(fsPath);
              stream.pipe(res);
              return;
            }
          } catch (err) {
            // ignore and fall through to next middleware
          }
          return next();
        });
      }
    },
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ],
  build: {
    target: 'esnext',
    minify: 'esbuild',
    cssMinify: true,
    assetsInlineLimit: 0, // Never inline video files
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'media-viewer': ['react-window', 'react-virtualized-auto-sizer'],
        },
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 3000, // Try a different port
    strictPort: false,
    host: true,
    headers: {
      'Cache-Control': 'no-cache',
      'Access-Control-Allow-Origin': '*'
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-window', 'react-virtualized-auto-sizer'],
  },
  // Configure asset handling
  assetsInclude: ['**/*.mp4', '**/*.webm', '**/*.mov'],
});

