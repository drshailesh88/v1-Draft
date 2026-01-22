'use client';

import { Button } from '@/components/ui/button';
import { HiOutlineSparkles } from 'react-icons/hi2';

export default function SidebarDocs() {
  return (
    <div className="relative flex flex-col items-center rounded-lg border border-zinc-200 px-3 py-4 dark:border-white/10">
      <div className="flex h-[54px] w-[54px] items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800">
        <HiOutlineSparkles className="h-6 w-6 text-zinc-950 dark:text-white" />
      </div>
      <div className="mb-3 flex w-full flex-col pt-4">
        <p className="mb-2.5 text-center text-lg font-bold text-zinc-950 dark:text-white">
          Upgrade to PRO
        </p>
        <p className="text-center text-sm font-medium text-zinc-500 dark:text-zinc-400">
          Get unlimited access to all features and priority support.
        </p>
      </div>
      <a href="/dashboard/settings">
        <Button className="mt-auto flex h-full w-[200px] items-center justify-center rounded-lg px-4 py-2.5 text-sm font-medium">
          Upgrade Now
        </Button>
      </a>
    </div>
  );
}
