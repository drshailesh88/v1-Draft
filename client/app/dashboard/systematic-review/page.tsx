import { getUserDetails, getUser } from '@/utils/supabase/queries';
import SystematicReview from '@/components/dashboard/systematic-review';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function SystematicReviewPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <SystematicReview user={user} userDetails={userDetails} />;
}
