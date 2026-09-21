#!/usr/bin/env python3
"""
Sensei Unified Self-Check System
A customizable application for generating math problems and testcases
"""

import json
import os
import random
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI
app = FastAPI(title="Sensei Unified Self-Check System", version="1.0.0")

# =====================
# Core Domain Models
# =====================

class ProblemType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    NUMERICAL = "numerical"
    PROOF = "proof"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class Problem:
    id: str
    type: ProblemType
    difficulty: Difficulty
    question: str
    correct_answer: Any
    explanation: str
    tags: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class TestCase:
    problem_id: str
    input_data: Dict[str, Any]
    expected_output: Any
    description: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class APIConfig:
    endpoint_url: str
    api_key: str
    timeout: int = 30
    rate_limit: int = 100

# =====================
# Problem Generator Interface
# =====================

class ProblemGenerator(ABC):
    @abstractmethod
    def generate(self, topic: str, difficulty: Difficulty, count: int = 1) -> List[Problem]:
        pass
    
    @abstractmethod
    def validate(self, answer: Any, problem: Problem) -> bool:
        pass

# =====================
# Math Problem Generators
# =====================

class AlgebraGenerator(ProblemGenerator):
    def __init__(self):
        self.topics = {
            "linear_equation": self._generate_linear,
            "quadratic_equation": self._generate_quadratic,
            "factoring": self._generate_factoring,
            "system_of_equations": self._generate_system
        }
    
    def generate(self, topic: str, difficulty: Difficulty, count: int = 1) -> List[Problem]:
        if topic not in self.topics:
            raise ValueError(f"Unknown topic: {topic}")
        
        problems = []
        for i in range(count):
            problem = self.topics[topic](difficulty, i)
            problems.append(problem)
        return problems
    
    def validate(self, answer: Any, problem: Problem) -> bool:
        try:
            return abs(float(answer) - float(problem.correct_answer)) < 0.0001
        except:
            return False
    
    def _generate_linear(self, difficulty: Difficulty, idx: int) -> Problem:
        coef_range = {"easy": (1, 10), "medium": (-20, 20), "hard": (-50, 50)}
        min_val, max_val = coef_range[difficulty.value]
        
        a = random.randint(min_val, max_val)
        if a == 0:
            a = 1
        b = random.randint(min_val, max_val)
        c = random.randint(min_val, max_val)
        
        # Solution: x = (c - b) / a
        solution = (c - b) / a
        
        question = f"Giải phương trình: {a}x + {b} = {c}"
        return Problem(
            id=f"algebra_linear_{difficulty.value}_{idx}_{hashlib.md5(str(a*b*c).encode()).hexdigest()[:8]}",
            type=ProblemType.SHORT_ANSWER,
            difficulty=difficulty,
            question=question,
            correct_answer=round(solution, 4),
            explanation=f"Phương trình {a}x + {b} = {c} có nghiệm x = {solution}",
            tags=["algebra", "linear", difficulty.value]
        )
    
    def _generate_quadratic(self, difficulty: Difficulty, idx: int) -> Problem:
        a = random.randint(1, 5)
        b = random.randint(-15, 15)
        c = random.randint(-20, 20)
        
        # Calculate discriminant
        discriminant = b*b - 4*a*c
        if discriminant < 0:
            # Generate with real roots instead
            root1 = random.randint(-5, 5)
            root2 = random.randint(-5, 5)
            a = random.randint(1, 5)
            b = -a * (root1 + root2)
            c = a * root1 * root2
            discriminant = b*b - 4*a*c
        
        sqrt_d = discriminant ** 0.5
        x1 = (-b + sqrt_d) / (2*a)
        x2 = (-b - sqrt_d) / (2*a)
        
        question = f"Giải phương trình bậc hai: {a}x² + {b}x + {c} = 0"
        answer = f"x₁ = {round(x1, 4)}, x₂ = {round(x2, 4)}"
        
        return Problem(
            id=f"algebra_quad_{difficulty.value}_{idx}_{hashlib.md5(str(a*b*c).encode()).hexdigest()[:8]}",
            type=ProblemType.SHORT_ANSWER,
            difficulty=difficulty,
            question=question,
            correct_answer=answer,
            explanation=f"Phương trình có nghiệm x₁ = {round(x1, 4)}, x₂ = {round(x2, 4)}",
            tags=["algebra", "quadratic", difficulty.value]
        )
    
    def _generate_factoring(self, difficulty: Difficulty, idx: int) -> Problem:
        a = random.randint(2, 5)
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        
        # Polynomial: a(x - r1)(x - r2) = ax² - a(r1+r2)x + ar1*r2
        b = -a * (r1 + r2)
        c = a * r1 * r2
        
        question = f"Phân tích thành nhân tử của: {a}x² + {b}x + {c}"
        answer = f"{a}(x - {r1})(x - {r2})"
        
        return Problem(
            id=f"algebra_factor_{difficulty.value}_{idx}",
            type=ProblemType.SHORT_ANSWER,
            difficulty=difficulty,
            question=question,
            correct_answer=answer,
            explanation=f"{a}x² + {b}x + {c} = {a}(x - {r1})(x - {r2})",
            tags=["algebra", "factoring", difficulty.value]
        )
    
    def _generate_system(self, difficulty: Difficulty, idx: int) -> Problem:
        a1 = random.randint(1, 5)
        b1 = random.randint(-5, 5)
        a2 = random.randint(1, 5)
        b2 = random.randint(-5, 5)
        
        # Solve system: a1*x + b1*y = c1, a2*x + b2*y = c2
        det = a1 * b2 - a2 * b1
        if det == 0:
            # Re-generate with different coefficients
            return self._generate_system(difficulty, idx)
        
        # Random solution
        x_sol = random.randint(-10, 10)
        y_sol = random.randint(-10, 10)
        
        c1 = a1 * x_sol + b1 * y_sol
        c2 = a2 * x_sol + b2 * y_sol
        
        question = f"Giải hệ phương trình:\n  {a1}x + {b1}y = {c1}\n  {a2}x + {b2}y = {c2}"
        
        return Problem(
            id=f"algebra_system_{difficulty.value}_{idx}",
            type=ProblemType.SHORT_ANSWER,
            difficulty=difficulty,
            question=question,
            correct_answer=f"x = {x_sol}, y = {y_sol}",
            explanation=f"Giải bằng phương pháp thay thế hoặc Cramer:\n  x = {x_sol}, y = {y_sol}",
            tags=["algebra", "system", difficulty.value]
        )

class GeometryGenerator(ProblemGenerator):
    def generate(self, topic: str, difficulty: Difficulty, count: int = 1) -> List[Problem]:
        problems = []
        for i in range(count):
            problems.append(self._generate_geometry(topic, difficulty, i))
        return problems
    
    def validate(self, answer: Any, problem: Problem) -> bool:
        try:
            return abs(float(answer) - float(problem.correct_answer)) < 0.0001
        except:
            return False
    
    def _generate_geometry(self, topic: str, difficulty: Difficulty, idx: int) -> Problem:
        if topic == "triangle_area":
            base = random.randint(5, 20)
            height = random.randint(5, 20)
            area = 0.5 * base * height
            
            question = f"Tính diện tích tam giác có đáy = {base} và chiều cao = {height}"
            return Problem(
                id=f"geom_triangle_{idx}",
                type=ProblemType.NUMERICAL,
                difficulty=difficulty,
                question=question,
                correct_answer=area,
                explanation=f"Diện tích = ½ * đáy * chiều cao = ½ * {base} * {height} = {area}",
                tags=["geometry", "triangle", difficulty.value]
            )
        
        elif topic == "circle":
            radius = random.randint(3, 15)
            pi = 3.14159
            area = pi * radius * radius
            perimeter = 2 * pi * radius
            
            question = f"Tính diện tích và chu vi của một tròn có bán kính R = {radius}"
            return Problem(
                id=f"geom_circle_{idx}",
                type=ProblemType.NUMERICAL,
                difficulty=difficulty,
                question=question,
                correct_answer=f"Diện tích = {round(area, 2)}, Chu vi = {round(perimeter, 2)}",
                explanation=f"Diện tích = πR² = {round(area, 2)}\nChu vi = 2πR = {round(perimeter, 2)}",
                tags=["geometry", "circle", difficulty.value]
            )
        
        else:
            # Default triangle area
            return self._generate_geometry("triangle_area", difficulty, idx)

# =====================
# Problem Generator Registry
# =====================

class GeneratorRegistry:
    def __init__(self):
        self._generators: Dict[str, ProblemGenerator] = {}
        self._api_configs: Dict[str, APIConfig] = {}
    
    def register(self, name: str, generator: ProblemGenerator, api_config: Optional[APIConfig] = None):
        self._generators[name] = generator
        if api_config:
            self._api_configs[name] = api_config
    
    def get_generator(self, name: str) -> Optional[ProblemGenerator]:
        return self._generators.get(name)
    
    def get_api_config(self, name: str) -> Optional[APIConfig]:
        return self._api_configs.get(name)
    
    def list_generators(self) -> List[str]:
        return list(self._generators.keys())

registry = GeneratorRegistry()

# Register default generators
registry.register("algebra", AlgebraGenerator())
registry.register("geometry", GeometryGenerator())

# =====================
# API Request/Response Models
# =====================

class ProblemRequest(BaseModel):
    type: str = Field(..., description="Problem type (multiple_choice, short_answer)")
    difficulty: str = Field(..., description="Difficulty level (easy, medium, hard)")
    topic: str = Field(..., description="Topic for the problem")
    count: int = Field(default=1, gt=0, le=20, description="Number of problems to generate")

class TestCaseRequest(BaseModel):
    problem_id: str
    input_format: Dict[str, Any]
    output_format: Dict[str, Any]
    count: int = Field(default=3, gt=0, le=20)

class ConfigUpdate(BaseModel):
    generator: str
    endpoint_url: str
    api_key: str
    timeout: Optional[int] = 30
    rate_limit: Optional[int] = 100

# =====================
# API Endpoints
# =====================

@app.get("/")
async def root():
    return {"name": "Sensei Unified Self-Check System", "version": "1.0.0", "status": "running"}

@app.get("/generators")
async def list_generators():
    return {"generators": registry.list_generators(), "total": len(registry.list_generators())}

@app.post("/generate/problem")
async def generate_problem(request: ProblemRequest):
    difficulty = Difficulty(request.difficulty.lower())
    
    if request.type.lower() == "multiple_choice":
        # Generate base problem and add choices
        pass
    
    # Find appropriate generator
    generator = None
    for name in ["algebra", "geometry"]:
        gen = registry.get_generator(name)
        if gen:
            generator = gen
            break
    
    if not generator:
        raise HTTPException(status_code=404, detail="No problem generator available")
    
    try:
        problems = generator.generate(request.topic.lower(), difficulty, request.count)
        return {
            "success": True,
            "problems": [p.to_dict() for p in problems],
            "count": len(problems)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate/testcase")
async def generate_testcase(request: TestCaseRequest):
    # Generate test cases for a problem
    test_cases = []
    for i in range(request.count):
        tc = TestCase(
            problem_id=request.problem_id,
            input_data=request.input_format,
            expected_output=request.output_format,
            description=f"Test case {i+1} for {request.problem_id}"
        )
        test_cases.append(tc.to_dict())
    
    return {"success": True, "test_cases": test_cases}

@app.post("/configure/api")
async def configure_api(config: ConfigUpdate):
    new_config = APIConfig(
        endpoint_url=config.endpoint_url,
        api_key=config.api_key,
        timeout=config.timeout or 30,
        rate_limit=config.rate_limit or 100
    )
    registry.register(config.generator, registry.get_generator(config.generator), new_config)
    return {"success": True, "message": f"API configured for {config.generator}"}

@app.post("/config")
async def update_config(config: ConfigUpdate):
    await configure_api(config)
    return {"success": True}

@app.get("/problems/{problem_id}")
async def get_problem(problem_id: str):
    # In production, this would fetch from database
    return {"problem_id": problem_id, "message": "Problem retrieved (placeholder)"}

@app.post("/validate")
async def validate_answer(problem_id: str, answer: Any):
    return {"valid": True, "problem_id": problem_id, "answer": answer}

# =====================
# CLI Interface
# =====================

def cli():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sensei Unified Self-Check System CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Generate problems
    gen_parser = subparsers.add_parser("generate", help="Generate problems")
    gen_parser.add_argument("--type", required=True, help="Problem type")
    gen_parser.add_argument("--difficulty", required=True, choices=["easy", "medium", "hard"])
    gen_parser.add_argument("--topic", required=True, help="Topic")
    gen_parser.add_argument("--count", type=int, default=1)
    
    # Start server
    server_parser = subparsers.add_parser("server", help="Start API server")
    server_parser.add_argument("--port", type=int, default=8000)
    server_parser.add_argument("--host", default="0.0.0.0")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        difficulty = Difficulty(args.difficulty)
        
        # Try algebra generator first, then geometry
        gen = registry.get_generator("algebra")
        if gen:
            try:
                problems = gen.generate(args.topic, difficulty, args.count)
            except ValueError:
                gen = registry.get_generator("geometry")
                if gen:
                    problems = gen.generate(args.topic.lower(), difficulty, args.count)
                else:
                    print("No generator available for this topic")
                    return
        else:
            gen = registry.get_generator("geometry")
            if gen:
                problems = gen.generate(args.topic.lower(), difficulty, args.count)
            else:
                print("No generator available")
                return
        
        for p in problems:
            print(f"\n--- Problem: {p.id} ---")
            print(f"Difficulty: {p.difficulty.value}")
            print(p.question)
            print(f"Answer: {p.correct_answer}")
            print(f"Explanation: {p.explanation}")
    
    elif args.command == "server":
        print(f"Starting server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()