'use client';

import { motion } from 'framer-motion';

type Post = { id: string; url: string; caption?: string };

export function BlurredGrid({ posts, blurred }: { posts: Post[]; blurred: boolean }) {
  return (
    <div className="grid grid-cols-3 gap-1 sm:gap-2">
      {posts.slice(0, 9).map((p, i) => (
        <motion.div
          key={p.id}
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.04, duration: 0.4 }}
          className="relative aspect-square overflow-hidden rounded-md bg-black"
        >
          <img
            src={p.url}
            alt=""
            className="h-full w-full object-cover transition-all duration-700"
            style={blurred ? { filter: 'blur(28px) saturate(0.9)', transform: 'scale(1.1)' } : {}}
            crossOrigin="anonymous"
          />
          {blurred && (
            <div className="absolute inset-0 bg-gradient-to-br from-black/10 via-transparent to-black/40" />
          )}
        </motion.div>
      ))}
    </div>
  );
}
