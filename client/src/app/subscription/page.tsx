'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'

interface Subscription {
  tier: string
  status: string
  payment_method: string
  currency: string
  amount: number
  started_at: string
  ends_at: string | null
}

const TIER_PRICES = {
  free: { USD: 0, EUR: 0, GBP: 0, INR: 0 },
  pro: { USD: 19, EUR: 17, GBP: 15, INR: 1599 },
  team: { USD: 49, EUR: 44, GBP: 39, INR: 4099 },
}

const TIER_FEATURES = {
  free: [
    'Basic literature search',
    '5 PDF uploads per month',
    'Standard citation generator',
    'Basic AI detection',
    'Limited chat interactions',
  ],
  pro: [
    'Advanced literature search',
    'Unlimited PDF uploads',
    'Full citation generator',
    'Advanced AI detection',
    'Unlimited chat interactions',
    'AI writing assistant',
    'Data extraction tools',
    'Priority support',
  ],
  team: [
    'Everything in Pro',
    'Team collaboration',
    'Admin dashboard',
    'Team analytics',
    'Bulk PDF processing',
    'API access',
    'Custom integrations',
    'Dedicated support',
  ],
}

export default function SubscriptionPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [currency, setCurrency] = useState('USD')
  const [paymentMethod, setPaymentMethod] = useState('auto')
  const [loadingSubscription, setLoadingSubscription] = useState(false)
  const [processingTier, setProcessingTier] = useState<string | null>(null)
  const [detectedCurrency, setDetectedCurrency] = useState('USD')
  const [cancelling, setCancelling] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    } else if (user) {
      fetchSubscription()
      detectCurrency()
    }
  }, [user, loading, router])

  const detectCurrency = async () => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/payments/currency`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setDetectedCurrency(data.currency)
        setCurrency(data.currency)
      }
    } catch (error) {
      console.error('Error detecting currency:', error)
    }
  }

  const fetchSubscription = async () => {
    setLoadingSubscription(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/payments/subscription`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setSubscription(data)
      }
    } catch (error) {
      console.error('Error fetching subscription:', error)
    } finally {
      setLoadingSubscription(false)
    }
  }

  const handleSubscribe = async (tier: string) => {
    if (tier === 'free') {
      await upgradeToFree()
      return
    }

    setProcessingTier(tier)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/payments/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tier,
          currency,
          payment_method: paymentMethod,
        }),
      })

      if (!res.ok) {
        throw new Error('Failed to create checkout')
      }

      const data = await res.json()
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      } else if (data.payment_provider === 'none') {
        await fetchSubscription()
      }
    } catch (error: any) {
      alert(error.message || 'Failed to start subscription')
    } finally {
      setProcessingTier(null)
    }
  }

  const upgradeToFree = async () => {
    setProcessingTier('free')
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/payments/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tier: 'free',
          currency: 'USD',
          payment_method: 'none',
        }),
      })

      if (res.ok) {
        await fetchSubscription()
      } else {
        throw new Error('Failed to upgrade to free')
      }
    } catch (error: any) {
      alert(error.message || 'Failed to upgrade')
    } finally {
      setProcessingTier(null)
    }
  }

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your billing period.')) {
      return
    }

    setCancelling(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/payments/cancel`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (res.ok) {
        await fetchSubscription()
        alert('Subscription cancelled successfully')
      } else {
        throw new Error('Failed to cancel subscription')
      }
    } catch (error: any) {
      alert(error.message || 'Failed to cancel subscription')
    } finally {
      setCancelling(false)
    }
  }

  if (loading || loadingSubscription) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      active: { variant: 'default' as const, text: 'Active' },
      cancelled: { variant: 'destructive' as const, text: 'Cancelled' },
      past_due: { variant: 'outline' as const, text: 'Past Due' },
    }
    const v = variants[status] || variants.active
    return <Badge variant={v.variant}>{v.text}</Badge>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Choose Your Plan</h1>
          <p className="text-xl text-gray-600">
            Unlock the full potential of your academic research
          </p>
        </div>

        {subscription && subscription.tier !== 'free' && (
          <Card className="mb-8 bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Current Subscription</p>
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-semibold capitalize">{subscription.tier} Plan</h3>
                    {getStatusBadge(subscription.status)}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {subscription.currency} {subscription.amount}/month via {subscription.payment_method}
                  </p>
                  {subscription.ends_at && (
                    <p className="text-sm text-gray-500 mt-1">
                      Renews on {new Date(subscription.ends_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                {subscription.status === 'active' && (
                  <Button
                    variant="destructive"
                    onClick={handleCancel}
                    disabled={cancelling}
                  >
                    {cancelling ? 'Cancelling...' : 'Cancel Subscription'}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="mb-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <div className="flex items-center gap-2">
            <label htmlFor="currency" className="text-sm font-medium text-gray-700">
              Currency:
            </label>
            <Select value={currency} onValueChange={setCurrency}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="USD">USD ($)</SelectItem>
                <SelectItem value="EUR">EUR (€)</SelectItem>
                <SelectItem value="GBP">GBP (£)</SelectItem>
                <SelectItem value="INR">INR (₹)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="paymentMethod" className="text-sm font-medium text-gray-700">
              Payment:
            </label>
            <Select value={paymentMethod} onValueChange={setPaymentMethod}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto-detect</SelectItem>
                <SelectItem value="paddle">Paddle (Global)</SelectItem>
                <SelectItem value="razorpay">Razorpay (India)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {detectedCurrency !== currency && (
            <Badge variant="outline" className="text-xs">
              Detected: {detectedCurrency}
            </Badge>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {Object.keys(TIER_PRICES).map((tier) => {
            const price = TIER_PRICES[tier as keyof typeof TIER_PRICES][currency as keyof typeof TIER_PRICES.free]
            const features = TIER_FEATURES[tier as keyof typeof TIER_FEATURES]
            const isActive = subscription?.tier === tier
            const isRecommended = tier === 'pro'

            return (
              <Card
                key={tier}
                className={`relative ${
                  isRecommended ? 'ring-2 ring-blue-500 scale-105' : ''
                } ${isActive ? 'bg-blue-50 border-blue-300' : ''}`}
              >
                {isRecommended && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-500">Most Popular</Badge>
                  </div>
                )}
                <CardHeader>
                  <CardTitle className="text-2xl capitalize">{tier}</CardTitle>
                  <CardDescription>
                    {price === 0 ? 'Free forever' : `${currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency === 'GBP' ? '£' : '₹'}${price}/month`}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <ul className="space-y-3">
                    {features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <svg
                          className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button
                    className="w-full"
                    variant={isActive ? 'outline' : 'default'}
                    onClick={() => handleSubscribe(tier)}
                    disabled={processingTier === tier || (isActive && tier !== 'free')}
                  >
                    {processingTier === tier
                      ? 'Processing...'
                      : isActive
                      ? 'Current Plan'
                      : tier === 'free'
                      ? 'Get Started'
                      : 'Subscribe'}
                  </Button>
                </CardFooter>
              </Card>
            )
          })}
        </div>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p className="mb-2">
            <strong>Paddle</strong> accepts Credit/Debit Cards, PayPal, Apple Pay, and Google Pay for global users
          </p>
          <p>
            <strong>Razorpay</strong> accepts UPI, Cards, Net Banking, Wallets, and EMI for Indian users
          </p>
          <p className="mt-4 text-xs">
            By subscribing, you agree to our Terms of Service and Privacy Policy. Cancel anytime from your account settings.
          </p>
        </div>
      </div>
    </div>
  )
}
