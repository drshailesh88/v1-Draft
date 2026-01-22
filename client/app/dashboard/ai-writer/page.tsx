import { getUserDetails, getUser } from '@/utils/supabase/queries';
import AIWriter from '@/components/dashboard/ai-writer';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function AIWriterPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <AIWriter user={user} userDetails={userDetails} />;
}
