from pydantic import BaseModel, ConfigDict, HttpUrl

# Schema for receiving the plan ID in the request body
class SubscriptionPlanId(BaseModel):
    plan_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

# Schema for the response of the checkout session creation
class StripeCheckoutSession(BaseModel):
    id: str
    url: HttpUrl

    model_config = ConfigDict(
        from_attributes=True,
    )
