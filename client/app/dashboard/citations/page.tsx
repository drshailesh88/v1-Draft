import { getUserDetails, getUser } from '@/utils/supabase/queries';
import CitationGenerator from '@/components/dashboard/citations';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function CitationsPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <CitationGenerator user={user} userDetails={userDetails} />;
}
