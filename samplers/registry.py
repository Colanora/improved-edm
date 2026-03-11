from sample import ResearchSampler
from samplers.euler import EulerSampler
from samplers.heun import HeunSampler

BUILTIN_SAMPLERS = {
    "euler": EulerSampler,
    "heun": HeunSampler,
    "research": ResearchSampler,
}
