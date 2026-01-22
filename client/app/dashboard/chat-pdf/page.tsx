import { getUserDetails, getUser } from '@/utils/supabase/queries';
import ChatPDF from '@/components/dashboard/chat-pdf';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export default async function ChatPDFPage() {
  const supabase = createClient();
  const [user, userDetails] = await Promise.all([
    getUser(supabase),
    getUserDetails(supabase)
  ]);

  if (!user) {
    return redirect('/dashboard/signin');
  }

  return <ChatPDF user={user} userDetails={userDetails} />;
}
