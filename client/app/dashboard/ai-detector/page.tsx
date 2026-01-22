import { getUserDetails, getUser } from '@/utils/supabase/queries';
import AIDetector from '@/components/dashboard/ai-detector';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function AIDetectorPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <AIDetector user={user} userDetails={userDetails} />;
}
