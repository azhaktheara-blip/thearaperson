from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from portfolio.models import Profile,Project,BlogPost

class Command(BaseCommand):
    help='Add fictional demo content without changing existing records.'
    @transaction.atomic
    def handle(self,*args,**options):
        if not Profile.objects.exists():
            Profile.objects.create(name='Alex Morgan',tagline='Independent designer & creative developer.',
                bio='I’m a Brooklyn-based designer and creative developer. I partner with ambitious people and thoughtful brands to turn complex challenges into clear, distinctive experiences. From the first sketch to the final line of code, I care about the details.',
                email='hello@example.com',location='Brooklyn, New York',social_links={},available=True)
        projects=[
            ('orbit','Orbit®','Brand identity','Strategy & design','A new perspective for a new generation of everyday explorers.','Orbit Studio','orbit','Figma, Illustrator, Art direction'),
            ('forma','Forma Living','Digital experience','Design & development','An elevated digital home for thoughtfully made objects.','Forma Living','forma','Django, JavaScript, Supabase, Figma'),
            ('aura','Aura Wellness','Brand identity','Strategy & design','A warmer, more human approach to feeling like yourself.','Aura Wellness','aura','Figma, Illustrator, Design systems'),
            ('mono','Mono Archive','Digital experience','Design & development','An independent cultural archive built for discovery.','Mono Archive','mono','Django, GSAP, PostgreSQL'),
        ]
        for index,(slug,title,category,role,summary,client,artwork,tech) in enumerate(projects):
            Project.objects.get_or_create(slug=slug,defaults=dict(title=title,summary=summary,category=category,role=role,
                client=client,artwork=artwork,tech_stack=tech,featured=True,display_order=index,year=2026 if index<2 else 2025,
                case_study=f'''## The challenge

{client} needed a clearer way to communicate what made its offering distinctive. The existing experience made people work too hard to understand the story, and the visual language lacked consistency across touchpoints.

Our starting point was simple: understand the audience before deciding what the design should look like.

## Finding the direction

We explored the relationship between clarity and character through a series of collaborative workshops. We mapped the key journeys, reviewed the existing content, and developed three visual directions grounded in the same strategic idea.

The chosen direction paired expressive typography with a restrained palette and a flexible grid. Every decision had to earn its place.

## From concept to experience

I built a modular system of components that could adapt across desktop and mobile. Motion was used to guide attention, while reduced-motion preferences and keyboard navigation shaped the implementation from the beginning.

- A flexible visual identity with clear usage rules
- Responsive layouts built around the content
- Reusable components for future expansion
- A straightforward content management workflow

## The outcome

The result is a cohesive, considered experience that gives the brand room to grow. This is a fictional demonstration project; the process and artwork illustrate the portfolio’s content capabilities rather than a real client engagement.

> Good design makes the next step feel obvious.
'''))
        posts=[
            ('design-that-feels-like-something','Design that feels like something.','On why the most memorable work makes room for a little humanity.','Design & perspective',
             '''## The things we remember

Think about the last website you remembered after closing the tab. It probably wasn’t because its grid was mathematically perfect. More likely, something about it felt specific: an unexpected detail, a useful interaction, a sentence that sounded like a person.

That feeling is a design decision, too.

## Clarity creates room for character

A strong foundation makes expressive choices possible. When navigation is obvious and the content has a clear hierarchy, we can afford to be more playful with typography, imagery, or motion. The useful and the memorable support each other.

I start with the questions a visitor brings: Where am I? Is this for me? What can I do next? Once those answers are clear, I look for the moments that can carry a little personality.

## Small things, considered

A hover state that responds at the right pace. A headline that has something to say. An error message that helps you recover. These small details add up to a larger impression of care.

The goal isn’t to make every moment remarkable. It is to make the whole experience feel intentional.

> Character works best when it grows out of purpose.

## Try this on your next project

Choose one interaction and describe how you want it to feel before you describe how it should look. Calm? Direct? Curious? That single word can become a useful test for the decisions that follow.
'''),
            ('less-but-better','A case for less, but better.','Finding clarity by giving every element a reason to be there.','Process & craft',
             '''## Subtraction is a design tool

When a page feels confusing, adding another explanation is tempting. Sometimes the better question is what can be removed.

Every element competes for attention. Removing an unnecessary label, redundant action, or decorative layer gives the important things more room to do their job.

## Begin with the task

Write down the single most important thing someone should be able to do on the page. Compare each element against that task. Some elements support it directly; others build the trust or context that makes it possible.

Anything else needs a good reason to stay.

## Keep the useful friction

Simplifying an interface doesn’t always mean reducing the number of clicks. A useful confirmation, a clear explanation of a choice, or an explicit form label can prevent confusion later.

Good simplicity respects the work a person is trying to do.

## Make space for the content

Let the content determine the rhythm. A short statement might need generous space. A detailed comparison might need a denser structure. Consistency matters, but the most useful systems know when to flex.
'''),
            ('design-and-code','Where design meets the browser.','Why I like staying close to both sides of the creative process.','Development',
             '''## The browser is part of the process

A static mockup is a useful conversation starter, but a website is something people interact with. It changes size, responds to input, and runs on devices with very different capabilities.

Building early makes those realities part of the design conversation.

## Prototype the uncertain parts

I don’t build every detail before agreeing on a direction. I build the parts that carry uncertainty: a complex layout, an interaction, or a content pattern that needs to work at several screen sizes.

A small working prototype often answers questions that another round of mockups cannot.

## Motion should explain

Animation is most useful when it helps people understand a relationship or notice a change. If an effect makes a task slower or harder to follow, it needs another pass.

I also treat reduced motion as a design input. The experience should remain clear and complete when the animations are removed.

## A shared language

Working across design and code helps me make better tradeoffs. I can recognize when an elegant visual idea introduces unnecessary complexity, and when a small technical investment opens up a better experience.

The best outcome is work that feels coherent from the first impression to the final interaction.
'''),
        ]
        for i,(slug,title,excerpt,tags,content) in enumerate(posts):
            BlogPost.objects.get_or_create(slug=slug,defaults=dict(title=title,excerpt=excerpt,tags=tags,content=content,published=True,published_at=timezone.now()-timedelta(days=7+i*10)))
        self.stdout.write(self.style.SUCCESS('Demo content is ready. Existing records were preserved.'))
