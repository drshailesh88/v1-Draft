// V1Draft Routes Configuration
import { IRoute } from '@/types/types';
import {
  HiOutlineHome,
  HiOutlineChatBubbleLeftRight,
  HiOutlineMagnifyingGlass,
  HiOutlineBookOpen,
  HiOutlineTableCells,
  HiOutlineShieldCheck,
  HiOutlinePencilSquare,
  HiOutlineClipboardDocumentList,
  HiOutlineSparkles,
  HiOutlineDocumentMagnifyingGlass,
  HiOutlineArrowPath,
  HiOutlineLightBulb,
  HiOutlineCog8Tooth,
} from 'react-icons/hi2';

export const routes: IRoute[] = [
  {
    name: 'Dashboard',
    path: '/dashboard/main',
    icon: <HiOutlineHome className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />,
    collapse: false
  },
  {
    name: 'Chat with PDF',
    path: '/dashboard/chat-pdf',
    icon: (
      <HiOutlineChatBubbleLeftRight className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Literature Search',
    path: '/dashboard/literature-search',
    icon: (
      <HiOutlineMagnifyingGlass className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Citation Generator',
    path: '/dashboard/citations',
    icon: (
      <HiOutlineBookOpen className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Data Extraction',
    path: '/dashboard/data-extraction',
    icon: (
      <HiOutlineTableCells className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'AI Detector',
    path: '/dashboard/ai-detector',
    icon: (
      <HiOutlineShieldCheck className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'AI Writer',
    path: '/dashboard/ai-writer',
    icon: (
      <HiOutlinePencilSquare className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Systematic Review',
    path: '/dashboard/systematic-review',
    icon: (
      <HiOutlineClipboardDocumentList className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Citation Booster',
    path: '/dashboard/citation-booster',
    icon: (
      <HiOutlineSparkles className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Paraphraser',
    path: '/dashboard/paraphraser',
    icon: (
      <HiOutlineArrowPath className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Deep Review',
    path: '/dashboard/deep-review',
    icon: (
      <HiOutlineDocumentMagnifyingGlass className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Find Topics',
    path: '/dashboard/find-topics',
    icon: (
      <HiOutlineLightBulb className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
  {
    name: 'Settings',
    path: '/dashboard/settings',
    icon: (
      <HiOutlineCog8Tooth className="-mt-[7px] h-4 w-4 stroke-2 text-inherit" />
    ),
    collapse: false
  },
];
