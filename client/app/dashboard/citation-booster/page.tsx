import { getUserDetails, getUser } from '@/utils/supabase/queries';
import CitationBooster from '@/components/dashboard/citation-booster';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function CitationBoosterPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <CitationBooster user={user} userDetails={userDetails} />;
}
