import { getUserDetails, getUser } from '@/utils/supabase/queries';
import Paraphraser from '@/components/dashboard/paraphraser';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function ParaphraserPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <Paraphraser user={user} userDetails={userDetails} />;
}
