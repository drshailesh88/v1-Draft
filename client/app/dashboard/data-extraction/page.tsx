import { getUserDetails, getUser } from '@/utils/supabase/queries';
import DataExtraction from '@/components/dashboard/data-extraction';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function DataExtractionPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <DataExtraction user={user} userDetails={userDetails} />;
}
