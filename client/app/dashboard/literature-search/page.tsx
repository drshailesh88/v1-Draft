import { getUserDetails, getUser } from '@/utils/supabase/queries';
import LiteratureSearch from '@/components/dashboard/literature-search';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function LiteratureSearchPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <LiteratureSearch user={user} userDetails={userDetails} />;
}
