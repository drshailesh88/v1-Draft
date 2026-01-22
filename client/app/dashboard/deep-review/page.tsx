import { getUserDetails, getUser } from '@/utils/supabase/queries';
import DeepReview from '@/components/dashboard/deep-review';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function DeepReviewPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <DeepReview user={user} userDetails={userDetails} />;
}
