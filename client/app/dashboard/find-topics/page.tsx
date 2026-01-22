import { getUserDetails, getUser } from '@/utils/supabase/queries';
import FindTopics from '@/components/dashboard/find-topics';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function FindTopicsPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <FindTopics user={user} userDetails={userDetails} />;
}
